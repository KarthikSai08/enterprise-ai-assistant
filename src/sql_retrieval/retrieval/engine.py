"""
Main retrieval pipeline orchestrator.

Pipeline steps:
  1. Domain classification (which business domains match the query)
  2. Query type classification (simple_agg / multi_table / ambiguous)
  3. BM25 sparse retrieval + BGE-M3 dense vector retrieval
  4. Reciprocal Rank Fusion (RRF) to combine both result sets
  5. Domain boost/penalty injection
  6. Keyword match boost
  7. Domain-table filtering (for single-domain queries)
  8. BGE Reranker cross-encoder re-ranking
  9. Score-gap cutoff (for simple_agg queries)
  10. Column matching and join-path resolution
"""

import re
import time
import math as _math  # used via __import__ in tanh normalization

from sql_retrieval.config import (
    AGG_KEYWORDS,
    AGGREGATION_TYPES,
    JOIN_KEYWORDS,
    SCORE_GAP_FACTOR,
    SCORE_THRESHOLD,
    STOPWORDS,
)
from sql_retrieval.retrieval.bm25 import BM25
from sql_retrieval.retrieval.reranker import Reranker
from sql_retrieval.retrieval.vector import VectorRetriever


class Retriever:
    def __init__(self, tables, domains, joins, col_syns):
        self.tables = tables     # {table_name: enriched_metadata}
        self.domains = domains   # {domain_name: {primary, support, trigger, anti}}
        self.joins = joins       # [{from, to, on, meaning}, ...]
        self.col_syns = col_syns # {"table.column": [synonyms]}

        # Build the searchable text for every table
        texts = {name: t["text"] for name, t in tables.items()}

        print("  Indexing BM25...")
        self.bm25 = BM25()
        self.bm25.index(texts)

        print("  Indexing Qdrant (BGE-M3)...")
        self.vector = VectorRetriever()
        self.vector.index(texts)

        self.reranker = Reranker()

    # ── Step 1: Domain matching ──────────────────────────────────────

    def _match_domains(self, query):
        """
        Score each domain by how many of its trigger keywords appear in the query.
        Also subtract for anti-keywords.
        Return a list of domain names whose score is ≥ 50% of the top scorer.
        """
        ql = query.lower()
        qw = set(ql.split())
        scores = {}

        for dn, dd in self.domains.items():
            s = 0
            for kw in dd["trigger"]:
                # Exact substring match = +10 (strong signal)
                if kw in ql:
                    s += 10
                else:
                    kws = kw.split()
                    # Multi-word trigger: all words present = +8
                    if len(kws) > 1 and all(w in qw for w in kws):
                        s += 8
                    # Single word trigger (>2 chars) = +8
                    elif len(kws) == 1 and len(kw) > 2 and kw in qw:
                        s += 8
            # Anti-keywords: if present, heavily penalize (-15)
            s -= sum(15 for ak in dd["anti"] if ak in ql)

            if s > 0:
                scores[dn] = s

        if not scores:
            return []

        # Keep domains within 50% of the top score
        ranked = sorted(scores.items(), key=lambda x: -x[1])
        threshold = ranked[0][1] * 0.5
        matched = [d for d, s in ranked if s >= threshold]

        # Heuristic: if both sales and purchase match, drop purchase
        # (sales is more common and often overshadows purchase)
        if "sales" in matched and "purchase" in matched:
            matched.remove("purchase")

        return matched if matched else ranked[:1]

    # ── Step 2: Query type classification ────────────────────────────

    def _classify_query(self, ql, domains):
        """
        Determine the query type, which controls how many tables we return:
          simple_agg  – aggregation like "total sales" → return at most 2 tables
          multi_table – comparison/breakdown queries → return up to 5 tables
          ambiguous   – everything else → return at most 2 tables
        """
        has_agg = any(kw in ql for kw in AGG_KEYWORDS)
        has_join_kw = any(kw in ql for kw in JOIN_KEYWORDS)
        single_domain = len(domains) == 1

        if has_agg and not has_join_kw and single_domain:
            return "simple_agg"
        if has_join_kw or len(domains) > 1:
            return "multi_table"
        return "ambiguous"

    # ── Relevance check ──────────────────────────────────────────────

    @staticmethod
    def _is_relevant(domain_hit, keyword_hit, top_score):
        """A query is relevant if any of: domain match, keyword match, high RRF score."""
        return domain_hit or keyword_hit or top_score >= 0.3

    # ── Main search pipeline ─────────────────────────────────────────

    def search(self, query: str) -> dict:
        """Full retrieval pipeline. Returns a structured dict with results, joins, context."""

        t0 = time.perf_counter()

        # Normalize the query: strip punctuation, collapse whitespace
        qn = re.sub(r"[^\w\s]", " ", query.lower()).strip()
        qn = re.sub(r"\s+", " ", qn)
        ql = query.lower()

        # ── Steps 1-2: Domain + type classification ──────────────────

        domains = self._match_domains(query)
        query_type = self._classify_query(qn, domains)

        # Number of tables to return depends on query type
        if query_type == "simple_agg":
            k = 2
        elif query_type == "ambiguous":
            k = 2
        else:
            k = 5

        rrf_k = max(k * 2, 3)        # candidates before reranker
        reranker_k = max(k, 2)        # candidates to rerank

        # ── Step 3: BM25 + Vector search ─────────────────────────────

        bm = self.bm25.search(qn, 10)
        vc = self.vector.search(qn, 10)

        # ── Step 4: Reciprocal Rank Fusion (RRF) ─────────────────────

        # RRF combines two ranked lists by their ranks rather than raw scores:
        #   score(n) = 1/(60+rank_bm) + 1/(60+rank_vec)
        # The constant 60 dampens rank differences so low-ranked items still contribute.
        rrf = {}
        for rank, (name, _) in enumerate(bm):
            rrf[name] = rrf.get(name, 0) + 1 / (60 + rank + 1)
        for rank, (name, _) in enumerate(vc):
            rrf[name] = rrf.get(name, 0) + 1 / (60 + rank + 1)

        # ── Step 5: Domain boost / penalty ───────────────────────────

        # Inject domain tables that didn't appear in search results,
        # and boost those that did. This ensures domain-relevant tables
        # are always considered.
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

        # ── Step 6: Keyword match boost ──────────────────────────────

        # Give +0.40 per matched keyword word for tables whose keywords
        # appear in the query
        qw = {w for w in ql.split() if w not in STOPWORDS}
        keyword_hit = False
        for name in rrf:
            tbl = self.tables.get(name, {})
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
                rrf[name] += 0.40 * len(matched_words)
                keyword_hit = True

        candidates = sorted(rrf.items(), key=lambda x: -x[1])[:rrf_k]

        # ── Step 7: Domain-table filtering (single-domain only) ──────

        # For single-domain queries, restrict results to that domain's
        # primary + support tables
        if len(domains) == 1:
            domain_tables = set()
            for t in self.domains.get(domains[0], {}).get("primary", []):
                domain_tables.add(t)
            for t in self.domains.get(domains[0], {}).get("support", []):
                domain_tables.add(t)
            candidates = [(n, s) for n, s in candidates if n in domain_tables]

        # ── Relevance gate ───────────────────────────────────────────

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

        # ── Step 8: BGE Reranker ─────────────────────────────────────

        reranked = self.reranker.rerank(
            query, candidates, rrf, self.tables, reranker_k
        )

        # ── Step 9: Score-gap cutoff (simple_agg only) ────────────────

        # If the second table's score is much lower than the first, keep only one
        if query_type == "simple_agg" and len(reranked) >= 2 and reranked[0][1] > 0:
            gap = reranked[1][1] / reranked[0][1]
            if gap < SCORE_GAP_FACTOR:
                reranked = reranked[:1]

        # ── Step 10: Build final results ─────────────────────────────

        # Normalize scores to [-1, 1] range using tanh
        results = []
        for name, score in reranked:
            sn = round(_math.tanh(score), 4)
            if sn < SCORE_THRESHOLD:
                continue
            if len(results) >= k:
                break
            t = self.tables.get(name, {})
            cols = self._match_columns(query, name, t.get("columns", []))
            results.append({
                "rank": len(results) + 1,
                "table": name,
                "score": sn,
                "domain": t.get("domain", ""),
                "columns": cols,
            })

        # ── Build debug / explanation string ─────────────────────────

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
                        if col_info and col_info.get("agg"):
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

        # Resolve join paths and build context string
        joins = self._match_joins(query, [r["table"] for r in results])
        ctx = self._build_context(results, joins)
        all_cols = list({c for r in results for c in r["columns"]})

        # Reason string for transparency
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

    # ── Column matching ──────────────────────────────────────────────

    def _match_columns(self, query, table_name, columns):
        """
        Score each column of a table against the query using:
          - Column name match (+10)
          - Business label match (+8 or +5)
          - Description word overlap (+3 each)
          - Column synonym match (+5 or +3)
          - Aggregation column bonus (+2)
        Returns the top 5 matching column names.
        """
        ql = query.lower()
        q_words = set(ql.split())
        scored = []

        for c in columns:
            s = 10 if c["name"].lower() in ql else 0

            # Business labels like "Invoice Date / Sale Date" are split on "/"
            if c.get("label"):
                label_parts = [p.strip().lower() for p in c["label"].split("/")]
                if any(p in ql for p in label_parts):
                    s += 8
                elif any(w in q_words for p in label_parts for w in p.split()):
                    s += 5

            # Description word overlap
            if c.get("desc"):
                s += sum(3 for w in c["desc"].lower().split() if w in ql)

            # Column synonyms (also check view → base table fallback)
            col_syns = self.col_syns.get(f"{table_name}.{c['name']}", [])
            if not col_syns and table_name.startswith("vw_"):
                base_tn = table_name.replace("vw_", "tbl_", 1)
                col_syns = self.col_syns.get(f"{base_tn}.{c['name']}", [])
            s += sum(5 for syn in col_syns if syn.lower() in ql)
            if any(w in q_words for syn in col_syns for w in syn.lower().split()):
                s += 3

            # Bonus for aggregation columns on aggregative queries
            if c.get("agg") and any(
                w in ql for w in ["total", "sum", "avg", "count", "amount", "revenue"]
            ):
                s += 2

            if s > 0:
                scored.append((c, s))

        scored.sort(key=lambda x: -x[1])
        return [c["name"] for c, s in scored if s > 0][:5]

    # ── Join-path matching ───────────────────────────────────────────

    def _match_joins(self, query, table_names):
        """
        Find join paths between the result tables that are relevant to the query.
        Relevance: how many words from the join's business meaning appear in the query.
        """
        ql = query.lower()
        ts = set(table_names)
        paths = [j for j in self.joins if j["from"] in ts and j["to"] in ts]
        scored = [
            (p, sum(3 for w in p["meaning"].split() if w in ql)) for p in paths
        ]
        scored.sort(key=lambda x: -x[1])
        return [p for p, _ in scored[:5]]

    # ── Context builder for LLM consumption ──────────────────────────

    def _build_context(self, results, joins):
        """
        Build a compact text representation of the results for downstream use.
        Format:
          table_name | cols={col1, col2} | purpose text
          joins: col1=col2  col3=col4
        """
        lines = []
        for r in results:
            t = self.tables.get(r["table"], {})
            purpose = t.get("purpose", "")
            cols = ", ".join(r["columns"]) if r["columns"] else "-"
            lines.append(f"{r['table']} | cols={{{cols}}} | {purpose}")
        if joins:
            parts = []
            for j in joins:
                p = j["on"].split("=")
                parts.append(f"{p[0].strip()}={p[1].strip()}")
            lines.append("joins: " + "  ".join(parts))
        return "\n".join(lines)
