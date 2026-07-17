import re
import time
import math as _math
import numpy as np
from collections import deque
from rapidfuzz import process, fuzz

from sql_retrieval.config import (
    AGG_KEYWORDS,
    AGGREGATION_TYPES,
    JOIN_KEYWORDS,
    SCORE_GAP_FACTOR,
    SCORE_THRESHOLD,
    STOPWORDS,
    TOP_K,
    RRF_K,
)
from sql_retrieval.metadata.loader import build
from sql_retrieval.retrieval.bm25 import BM25
from sql_retrieval.retrieval.reranker import Reranker
from sql_retrieval.retrieval.vector import VectorRetriever

COLUMN_RRF_K = 60
COLUMN_TOP_K = 15

_NEVER_CORRECT = frozenset({
    "the", "and", "for", "are", "but", "not", "you", "all", "can",
    "has", "had", "was", "were", "been", "get", "got", "did", "use",
    "show", "list", "get", "give", "find", "tell", "me",
    "how", "why", "what", "when", "where", "which",
    "performance",
})


class Retriever:
    def __init__(self, data=None):
        if data is None:
            data = build()

        self.tables = data["tables"]
        self.domains = data["domains"]
        self.joins = data["joins"]
        self.fk_graph: dict[str, set[str]] = {}
        for j in self.joins:
            self.fk_graph.setdefault(j["from"], set()).add(j["to"])
            self.fk_graph.setdefault(j["to"], set()).add(j["from"])
        self.col_syns = data["col_syns"]
        self.glossary = data.get("glossary", {})
        self.rules = data.get("rules", [])
        # Build glossary expansion map
        self._glossary_expansion: dict[str, list[str]] = {}
        for term, info in self.glossary.items():
            synonyms = info.get("synonyms", []) if isinstance(info, dict) else []
            for syn in synonyms:
                self._glossary_expansion.setdefault(syn.lower(), []).append(term.lower())

        texts = {name: t["text"] for name, t in self.tables.items()}

        print("  Indexing BM25...")
        self.bm25 = BM25()
        self.bm25.index(texts)

        print("  Indexing Qdrant (BGE-M3)...")
        self.vector = VectorRetriever()
        self.vector.index_tables(texts)

        self.reranker = Reranker()

        self.column_texts = data.get("column_texts", {})
        if self.column_texts:
            print("  Indexing BM25 columns...")
            self.bm25_columns = BM25()
            self.bm25_columns.index(self.column_texts)
            print("  Indexing ChromaDB columns...")
            self.vector.index_columns(self.column_texts)
        else:
            self.bm25_columns = BM25()

        self._all_terms: set[str] = set()
        for t in self.tables.values():
            for w in t.get("text", "").lower().split():
                cw = re.sub(r"[^a-z0-9]", "", w)
                if len(cw) >= 3:
                    self._all_terms.add(cw)
            self._all_terms.add(re.sub(r"[^a-z0-9]", "", t["name"].lower()))
            for kw in t.get("search_keywords", []):
                self._all_terms.add(re.sub(r"[^a-z0-9]", "", kw.lower()))
            for intent in t.get("common_user_intents", []):
                for w in intent.lower().split():
                    cw = re.sub(r"[^a-z0-9]", "", w)
                    if len(cw) >= 3:
                        self._all_terms.add(cw)
        for col_key, col_text in self.column_texts.items():
            for w in col_text.lower().split():
                cw = re.sub(r"[^a-z0-9]", "", w)
                if len(cw) >= 3:
                    self._all_terms.add(cw)
            self._all_terms.add(col_key.lower())
            if "." in col_key:
                col_name = col_key.split(".", 1)[1]
                self._all_terms.add(re.sub(r"[^a-z0-9]", "", col_name))
        for dn, dd in self.domains.items():
            self._all_terms.add(dn.lower())
            for w in dd.get("description", "").lower().split():
                cw = re.sub(r"[^a-z0-9]", "", w)
                if len(cw) >= 3:
                    self._all_terms.add(cw)
            for kw in dd.get("trigger", []):
                self._all_terms.add(re.sub(r"[^a-z0-9]", "", kw.lower()))
        for term in self.glossary:
            self._all_terms.add(re.sub(r"[^a-z0-9]", "", term.lower()))
            syns = self.glossary[term]
            if isinstance(syns, dict):
                for s in syns.get("synonyms", []):
                    self._all_terms.add(re.sub(r"[^a-z0-9]", "", s.lower()))

        self.domain_centroids: dict[str, np.ndarray] = {}
        if self.domains and hasattr(self.vector, "encoder"):
            for dn, dd in self.domains.items():
                texts = [dd.get("description", "")]
                texts.extend(dd.get("trigger", []))
                texts = [t for t in texts if t.strip()]
                if not texts:
                    continue
                vecs = self.vector.encoder.encode(texts, batch_size=8)["dense_vecs"]
                self.domain_centroids[dn] = np.mean(vecs, axis=0)
            print(f"  Built {len(self.domain_centroids)} domain centroids")

    def _correct_query_typos(self, query: str) -> str:
        tokens = query.lower().split()
        corrected = []
        for token in tokens:
            if len(token) <= 2 or token in _NEVER_CORRECT:
                corrected.append(token)
                continue
            best = process.extractOne(
                token, self._all_terms,
                scorer=fuzz.ratio,
                score_cutoff=80,
            )
            corrected.append(best[0] if best else token)
        return " ".join(corrected)

    def _expand_query(self, query: str) -> str:
        ql = query.lower()
        expansions = []
        for syn, terms in self._glossary_expansion.items():
            if syn in ql:
                expansions.extend(terms)
        if expansions:
            return query + " " + " ".join(expansions)
        return query

    def _detect_domain(self, query: str) -> list[str]:
        if self.domain_centroids:
            qvec = self.vector.encoder.encode([query], batch_size=8)["dense_vecs"][0]
            scores = {}
            for dn, centroid in self.domain_centroids.items():
                norm = np.linalg.norm(qvec) * np.linalg.norm(centroid)
                sim = float(np.dot(qvec, centroid) / norm) if norm else 0.0
                if sim >= 0.20:
                    scores[dn] = sim
            if scores:
                ranked = sorted(scores.items(), key=lambda x: -x[1])
                matched = [d for d, _ in ranked]
                if "sales" in matched and "purchase" in matched:
                    matched.remove("purchase")
                return matched[:3]
        if self.domains:
            return self._match_domains_from_files(query)
        return self._match_domains_from_tables(query)

    def _match_domains_from_files(self, query: str) -> list[str]:
        ql = query.lower()
        qw = set(ql.split())
        scores = {}

        for dn, dd in self.domains.items():
            s = 0
            for kw in dd.get("trigger", []):
                if kw in ql:
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
        if "sales" in matched and "purchase" in matched:
            matched.remove("purchase")
        return matched if matched else [d for d, _ in ranked[:1]]

    def _match_domains_from_tables(self, query: str) -> list[str]:
        ql = query.lower()
        domain_scores: dict[str, int] = {}
        for name, t in self.tables.items():
            domain = t.get("domain", "")
            if not domain:
                continue
            kws = t.get("search_keywords", [])
            for kw in kws:
                if kw.lower() in ql:
                    domain_scores[domain] = domain_scores.get(domain, 0) + 1
        if not domain_scores:
            return []
        ranked = sorted(domain_scores.items(), key=lambda x: -x[1])
        return [d for d, _ in ranked[:3]]

    def _classify_query(self, ql: str, domains: list[str]) -> str:
        has_agg = any(kw in ql for kw in AGG_KEYWORDS)
        has_join_kw = any(kw in ql for kw in JOIN_KEYWORDS)
        single_domain = len(domains) == 1

        if has_agg and not has_join_kw and single_domain:
            return "simple_agg"
        if has_join_kw or len(domains) > 1:
            return "multi_table"
        return "ambiguous"

    @staticmethod
    def _is_relevant(domain_hit: bool, keyword_hit: bool, top_score: float) -> bool:
        return domain_hit or keyword_hit or top_score >= 0.3

    def search(self, query: str) -> dict:
        t0 = time.perf_counter()

        qn = re.sub(r"[^\w\s]", " ", query.lower()).strip()
        qn = re.sub(r"\s+", " ", qn)
        ql = query.lower()

        expanded = self._expand_query(query)
        corrected = self._correct_query_typos(expanded)

        domains = self._detect_domain(corrected)
        query_type = self._classify_query(qn, domains)

        if query_type == "simple_agg":
            k = 2
        elif query_type == "ambiguous":
            k = 2
        else:
            k = 5

        # Use larger candidate pool to avoid missing keyword-only matches
        candidate_pool = max(k * 5, 30)
        rrf_k = max(k * 2, 3)
        reranker_k = max(k, 2)

        bm = self.bm25.search(corrected, candidate_pool)
        vc = self.vector.search_tables(corrected, TOP_K)

        rrf = {}
        for rank, (name, _) in enumerate(bm):
            rrf[name] = rrf.get(name, 0) + 1 / (RRF_K + rank + 1)
        for rank, (name, _) in enumerate(vc):
            rrf[name] = rrf.get(name, 0) + 1 / (RRF_K + rank + 1)

        # Domain gating — keep only tables from matched domains
        if domains:
            domain_table_set = set()
            for dn in domains:
                dm = self.domains.get(dn, {})
                domain_table_set.update(dm.get("primary", []))
                domain_table_set.update(dm.get("support", []))
            if domain_table_set:
                rrf = {k: v for k, v in rrf.items() if k in domain_table_set}

        # Domain boost
        max_rrf = max(rrf.values()) if rrf else 0.50
        for dn in domains:
            dm = self.domains.get(dn, {})
            for t in dm.get("primary", []) + dm.get("support", []):
                is_primary = t in dm.get("primary", [])
                floor = 0.50 if is_primary else 0.40
                if t in rrf:
                    if query_type == "simple_agg" and len(domains) == 1:
                        if not is_primary:
                            rrf[t] = max(rrf[t], floor)
                        else:
                            rrf[t] = max(rrf[t], max_rrf * 0.85, floor)
                    else:
                        rrf[t] = max(rrf[t], max_rrf * 0.75, floor)
                else:
                    rrf[t] = max(max_rrf * 0.65, floor)

        # Keyword match boost - check ALL tables, not just BM25/vector results
        qw = {w for w in ql.split() if w not in STOPWORDS}
        keyword_hit = False
        keyword_scores = {}
        for name, tbl in self.tables.items():
            kws = [k.lower() for k in tbl.get("keywords", []) if len(k) > 2]
            matched_words = set()
            for kw in kws:
                if kw in ql:
                    matched_words.add(kw)
                else:
                    kw_words = [w for w in kw.split() if len(w) > 2]
                    if len(kw_words) >= 2 and all(w in qw for w in kw_words):
                        matched_words.add("__multi__" + kw)
                    for w in kw_words:
                        if w in qw:
                            matched_words.add(w)
                        elif any(
                            wq.startswith(w) or w.startswith(wq) for wq in qw
                        ):
                            matched_words.add(w)
            if matched_words:
                keyword_scores[name] = len(matched_words)
                keyword_hit = True

        # Merge keyword scores into RRF
        for name, mcount in keyword_scores.items():
            boost = 0.50 * mcount
            if name in rrf:
                rrf[name] += boost
            else:
                rrf[name] = boost + 0.01  # small base to allow ranking

        candidates = sorted(rrf.items(), key=lambda x: -x[1])[:rrf_k]

        top_score = candidates[0][1] if candidates else 0
        domain_hit = bool(domains)
        relevant = self._is_relevant(domain_hit, keyword_hit, top_score)

        if not relevant:
            return {
                "query": query,
                "normalized": qn,
                "domains": domains,
                "relevant": False,
                "message": "I don't have relevant context to answer this question.",
                "results": [],
                "joins": [],
                "context": "",
                "columns_fetched": [],
                "table_count": 0,
                "_debug": "",
                "latency_ms": round((time.perf_counter() - t0) * 1000, 1),
            }

        reranked = self.reranker.rerank(
            query, candidates, rrf, self.tables, reranker_k
        )

        # Normalize reranker scores to (0, 1) via tanh for consistent thresholds
        reranked = [(name, round(_math.tanh(score), 4)) for name, score in reranked]

        if query_type == "simple_agg" and len(reranked) >= 2 and reranked[0][1] > 0:
            gap = reranked[1][1] / reranked[0][1]
            if gap < SCORE_GAP_FACTOR:
                reranked = reranked[:1]

        # Stage B: Column-level retrieval within candidate tables
        col_lookup: dict[str, list[str]] = {}
        if self.column_texts:
            candidate_tables = [r[0] for r in reranked]
            column_results = self._retrieve_columns(corrected, candidate_tables)
            for col_key, _ in column_results:
                parts = col_key.split(".", 1)
                if len(parts) == 2:
                    tbl, col = parts
                    col_lookup.setdefault(tbl, []).append(col)

        results = []
        for name, score in reranked:
            if score < SCORE_THRESHOLD:
                continue
            if len(results) >= k:
                break
            t = self.tables.get(name, {})
            cols = col_lookup.get(name) or self._match_columns(query, name, t.get("columns", []))

            # Collect relevant joins for this table
            table_joins = [
                j for j in self.joins
                if j["from"] == name or j["to"] == name
            ][:3]

            # Collect matching business rules
            matching_rules = []
            for rule in self.rules:
                affected = rule.get("tables", [])
                if name in affected:
                    matching_rules.append(rule.get("description", ""))

            results.append({
                "rank": len(results) + 1,
                "table": name,
                "display_name": t.get("display_name", ""),
                "score": score,
                "domain": t.get("domain", ""),
                "description": t.get("description", ""),
                "columns": cols,
                "all_columns": [c["name"] for c in t.get("columns", [])],
                "important_columns": t.get("important_columns", []),
                "common_filters": t.get("common_filters", []),
                "common_groupby": t.get("common_groupby", []),
                "suggested_joins": table_joins,
                "matching_rules": matching_rules,
                "primary_key": t.get("primary_key", ""),
                "foreign_keys": t.get("foreign_keys", []),
                "estimated_rows": t.get("estimated_rows", 0),
            })

        # Build debug
        matched_ops = []
        for kw, label in AGGREGATION_TYPES.items():
            if kw in ql:
                matched_cols = []
                for r in results:
                    for c in r["columns"]:
                        col_info = next(
                            (
                                x
                                for x in self.tables.get(r["table"], {}).get("columns", [])
                                if x["name"] == c
                            ),
                            None,
                        )
                        if col_info and col_info.get("aggregatable"):
                            matched_cols.append(f"{r['table']}.{c}")
                if matched_cols:
                    matched_ops.append(f"{label}({', '.join(matched_cols)})")
                else:
                    matched_ops.append(label)

        debug_parts = []
        if matched_ops:
            debug_parts.append(f"ops={' '.join(matched_ops)}")
        if domains:
            debug_parts.append(f"domain={','.join(domains)}")
        top_tables = [r["table"] for r in results]
        if top_tables:
            debug_parts.append(f"tables={' '.join(top_tables)}")

        joins = self._match_joins(query, [r["table"] for r in results])
        ctx = self._build_context(results, joins)
        all_cols = list({c for r in results for c in r["columns"]})

        reasons = []
        if domain_hit:
            reasons.append("domain")
        if keyword_hit:
            reasons.append("keyword")
        if top_score >= 0.3:
            reasons.append(f"rrf>=0.3 (score={top_score:.2f})")
        reasons.append(f"type={query_type}(k={k})")
        reason_str = "+".join(reasons) if reasons else "unknown"
        debug_str = " | ".join(debug_parts) if debug_parts else ""

        return {
            "query": query,
            "normalized": qn,
            "domains": domains,
            "_reason": reason_str,
            "_debug": debug_str,
            "results": results,
            "joins": joins,
            "context": ctx,
            "columns_fetched": all_cols,
            "table_count": len(results),
            "latency_ms": round((time.perf_counter() - t0) * 1000, 1),
            "query_type": query_type,
        }

    def _retrieve_columns(self, query: str, candidate_tables: list[str], top_k=COLUMN_TOP_K):
        bm = self.bm25_columns.search(query, top_k * 3)
        vc = self.vector.search_columns(query, top_k * 3)
        candidate_set = set(candidate_tables)
        bm_f = [(k, s) for k, s in bm if k.split(".")[0] in candidate_set]
        vc_f = [(k, s) for k, s in vc if k.split(".")[0] in candidate_set]
        rrf = {}
        for rank, (name, _) in enumerate(bm_f):
            rrf[name] = rrf.get(name, 0) + 1 / (COLUMN_RRF_K + rank + 1)
        for rank, (name, _) in enumerate(vc_f):
            rrf[name] = rrf.get(name, 0) + 1 / (COLUMN_RRF_K + rank + 1)
        candidates = sorted(rrf.items(), key=lambda x: -x[1])[:top_k]
        return self.reranker.rerank_columns(
            query, candidates, self.column_texts, top_k
        )

    def _match_columns(self, query: str, table_name: str, columns: list[dict]) -> list[str]:
        ql = query.lower()
        q_words = set(ql.split())
        scored = []

        for c in columns:
            s = 10 if c["name"].lower() in ql else 0

            # Display name match
            display = c.get("display_name", "")
            if display:
                display_parts = [p.strip().lower() for p in display.split("/")]
                if any(p in ql for p in display_parts):
                    s += 8
                elif any(w in q_words for p in display_parts for w in p.split()):
                    s += 5

            # Description word overlap
            desc = c.get("description", "")
            if desc:
                s += sum(3 for w in desc.lower().split() if w in ql)

            # Alias match
            aliases = c.get("aliases", [])
            s += sum(5 for a in aliases if a.lower() in ql)
            if any(w in q_words for a in aliases for w in a.lower().split()):
                s += 3

            # Col synonym fallback
            col_syns = self.col_syns.get(f"{table_name}.{c['name']}", [])
            s += sum(5 for syn in col_syns if syn.lower() in ql)

            # Aggregatable bonus
            if c.get("aggregatable") and any(
                w in ql for w in ["total", "sum", "avg", "count", "amount", "revenue"]
            ):
                s += 2

            if s > 0:
                scored.append((c, s))

        scored.sort(key=lambda x: -x[1])
        return [c["name"] for c, s in scored if s > 0][:5]

    def _bfs_path(self,start : str, end: str, max_depth : int):
        if start == end:
            return [start]
        visited = {start}
        queue = deque([[start]])
        while queue:
            path = queue.popleft()
            if len(path) - 1 >= max_depth:
                continue
            for neighbor in self.fk_graph.get(path[-1], ()):
                if neighbor == end:
                    return path + [neighbor]
                if neighbor not in visited:
                    visited.add(neighbor)
                    queue.append(path + [neighbor])
        return None

    def _find_bridge_tables(self, candidate_names : set, max_depth : int = 2) -> set:
        bridges = set()
        names = list(candidate_names)
        for i, a in enumerate(names):
            for b in names[i + 1:]:
                path = self._bfs_path(a, b, max_depth)
                if path :
                    for node in path[1:-1]:
                        if node in candidate_names:
                            bridges.add(node)

        return bridges

    def _match_joins(self, query: str, table_names: list[str]) -> list[dict]:
        ql = query.lower()
        ts = set(table_names)

        # If we have explicit join data, use it
        if self.joins:
            bridge_tables = self._find_bridge_tables(ts, max_depth=2)
            ts_expanded = ts | bridge_tables
            paths = [j for j in self.joins if j["from"] in ts_expanded and j["to"] in ts_expanded]
            scored = [
                (p, sum(3 for w in p["meaning"].split() if w in ql)) for p in paths
            ]
            scored.sort(key=lambda x: -x[1])
            return [p for p, _ in scored[:5]]

        # Otherwise infer from foreign_keys
        inferred = []
        for name in table_names:
            t = self.tables.get(name, {})
            for fk in t.get("foreign_keys", []):
                ref = fk.get("references", "")
                if "." in ref:
                    ref_table = ref.split(".")[0]
                    if ref_table in ts and ref_table != name:
                        inferred.append({
                            "from": name,
                            "to": ref_table,
                            "on": f"{name}.{fk['name']} = {ref}",
                            "meaning": fk.get("name", ""),
                            "join_type": "INNER",
                        })
        return inferred[:5]

    def _build_context(self, results: list[dict], joins: list[dict]) -> str:
        lines = []
        for r in results:
            display = r.get("display_name", "")
            cols = ", ".join(r["columns"]) if r["columns"] else "-"
            desc = r.get("description", "")[:100]
            domain = r.get("domain", "")
            header = f"{r['table']}"
            if display:
                header += f" ({display})"
            if domain:
                header += f" [{domain}]"
            lines.append(f"{header} | cols={{{cols}}} | {desc}")

            # Include important columns hint
            imp = r.get("important_columns", [])
            if imp:
                lines.append(f"  important: {', '.join(imp[:6])}")

        if joins:
            parts = []
            for j in joins:
                on = j.get("on", "")
                meaning = j.get("meaning", "")
                entry = on
                if meaning:
                    entry += f" ({meaning})"
                parts.append(entry)
            lines.append("joins: " + "  ".join(parts))

        # Append matching rules
        all_rules = []
        for r in results:
            for rule in r.get("matching_rules", []):
                if rule not in all_rules:
                    all_rules.append(rule)
        if all_rules:
            lines.append("rules: " + "; ".join(all_rules[:3]))

        return "\n".join(lines)
