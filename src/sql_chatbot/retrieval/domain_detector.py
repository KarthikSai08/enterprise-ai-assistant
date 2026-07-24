import re
import numpy as np
from sql_chatbot.config import DOMAIN_SIM_MIN_ABS, DOMAIN_SIM_GAP, DOMAIN_FILE_FALLBACK_FLOOR

class DomainDetector:
    def __init__(self, domains: dict, tables: dict, encoder=None):
        self.domains = domains
        self.tables = tables
        self._encoder = encoder
        self.domain_centroids: dict[str, np.ndarray] = {}
        if domains and encoder:
            for dn, dd in domains.items():
                texts_list = [dd.get("description", "")]
                texts_list.extend(dd.get("trigger", []))
                texts_list = [t for t in texts_list if t.strip()]
                if not texts_list:
                    continue
                vecs = encoder.encode(texts_list, batch_size=8)["dense_vecs"]
                self.domain_centroids[dn] = np.mean(vecs, axis=0)

    @property
    def centroid_count(self) -> int:
        return len(self.domain_centroids)

    def detect(self, query: str, query_vec=None) -> list[str]:
        if self.domain_centroids and self._encoder:
            qvec = query_vec if query_vec is not None else self._encoder.encode([query], batch_size=8)["dense_vecs"][0]
            scores = {}
            for dn, centroid in self.domain_centroids.items():
                norm = np.linalg.norm(qvec) * np.linalg.norm(centroid)
                sim = float(np.dot(qvec, centroid) / norm) if norm else 0.0
                scores[dn] = sim
            if scores:
                matched = self._filter_by_similarity(scores, query)
                if matched:
                    return matched[:3]
        if self.domains:
            return self._match_from_keywords(query)
        return self._match_from_tables(query)

    def _filter_by_similarity(self, scores: dict[str, float], query: str) -> list[str] | None:
        top_sim = max(scores.values())
        filtered = {d: s for d, s in scores.items() if s >= max(DOMAIN_SIM_MIN_ABS, top_sim - DOMAIN_SIM_GAP)}
        if not filtered:
            return None
        file_matched = set(self._match_from_keywords(query))
        if file_matched:
            filtered = {d: s for d, s in filtered.items() if s >= DOMAIN_FILE_FALLBACK_FLOOR or d in file_matched}
        if not filtered:
            return None
        ranked = sorted(filtered.items(), key=lambda x: -x[1])
        matched = [d for d, _ in ranked]
        return matched

    def _match_from_keywords(self, query: str) -> list[str]:
        ql = query.lower()
        qw = set(ql.split())
        scores = {}
        for dn, dd in self.domains.items():
            s = 0
            for kw in dd.get("trigger", []):
                if len(kw) <= 3:
                    if re.search(rf"\b{re.escape(kw)}\b", ql):
                        s += 10
                elif kw in ql:
                    s += 10
                else:
                    kws = kw.split()
                    if len(kws) > 1 and all(w in qw for w in kws):
                        s += 8
                    elif len(kws) == 1 and len(kw) > 2 and kw in qw:
                        s += 8
            s -= sum(15 for ak in dd.get("anti", []) if ak in ql)
            if s > 0:
                scores[dn] = s
        if not scores:
            return []
        ranked = sorted(scores.items(), key=lambda x: -x[1])
        threshold = ranked[0][1] * 0.5
        matched = [d for d, s in ranked if s >= threshold]
        return matched if matched else [d for d, _ in ranked[:1]]

    def _match_from_tables(self, query: str) -> list[str]:
        ql = query.lower()
        domain_scores: dict[str, int] = {}
        for name, t in self.tables.items():
            domain = t.get("domain", "")
            if not domain:
                continue
            for kw in t.get("all_search_terms", []):
                if kw.lower() in ql:
                    domain_scores[domain] = domain_scores.get(domain, 0) + 1
        if not domain_scores:
            return []
        ranked = sorted(domain_scores.items(), key=lambda x: -x[1])
        return [d for d, _ in ranked[:3]]

    def get_domain_table_set(self, domains: list[str]) -> set[str]:
        result = set()
        for dn in domains:
            dm = self.domains.get(dn, {})
            result.update(dm.get("primary", []))
            result.update(dm.get("support", []))
        return result
