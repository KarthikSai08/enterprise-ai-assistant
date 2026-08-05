import logging
import re
import time

from sql_chatbot.config import (
    GENERIC_COLUMN_NAMES,AGGREGATION_TYPES,
    SCORE_GAP_FACTOR,SCORE_THRESHOLD,
    KEYWORD_SCORE_THRESHOLD,KEYWORD_SCORE_PER_MATCH,
    KEYWORD_NULL_TABLE_BASE,STOPWORDS,
    TOP_K,RRF_K,
    COLUMN_RRF_K,COLUMN_TOP_K,
    CANDIDATE_POOL_MULTIPLIER,CANDIDATE_POOL_MIN,
    RRF_K_MULTIPLIER,RRF_K_MIN,
    RERANKER_K_MULTIPLIER,RERANKER_K_MIN,
    CE_WEIGHT,RRF_WEIGHT,
    DOMAIN_BOOST_FACTOR,DOMAIN_BOOST_FLOOR,
    DB_SERVER,DB_NAME,DB_USER,
    DB_PASS, DB_USE_WINDOWS_AUTH,DB_SCHEMA,
)
from flashtext2 import KeywordProcessor
from sql_chatbot.metadata.loader import build
from sql_chatbot.retrieval.bm25 import BM25
from sql_chatbot.retrieval.reranker import Reranker
from sql_chatbot.retrieval.vector import VectorRetriever
from sql_chatbot.retrieval.preprocessor import QueryPreprocessor
from sql_chatbot.retrieval.domain_detector import DomainDetector
from sql_chatbot.retrieval.join_graph import JoinGraph
from sql_chatbot.intent.detector import detect_intent
from sql_chatbot.retrieval.entity_value_extractor import EntityValueExtractor, _VALUE_CORRECTIONS_LOWER
from sql_chatbot.retrieval.value_filter_extractor import extract_value_filters

logger = logging.getLogger(__name__)


def _configure_logging():
    if not logging.getLogger().hasHandlers():
        logging.basicConfig(
            level=logging.INFO,
            format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
            datefmt="%H:%M:%S",
        )


_configure_logging()

class Retriever:
    def __init__(self, data=None):
        if data is None:
            data = build()

        self.tables = data["tables"]
        self.domains = data["domains"]
        self.joins = data["joins"]
        self.col_syns = data["col_syns"]
        self.glossary = data.get("glossary", {})
        self.rules = data.get("rules", [])
        self.column_texts = data.get("column_texts", {})
        self.join_graph = JoinGraph(self.joins, self.tables)
        self.entity_value_extractor = EntityValueExtractor(self.tables)

        texts = {name: t["text"] for name, t in self.tables.items()}

        logger.debug("Indexing BM25...")
        self.bm25 = BM25()
        self.bm25.index(texts)

        logger.debug("Indexing ChromaDB (BGE-M3)...")
        self.vector = VectorRetriever()
        self.vector.index_tables(texts)

        self.reranker = Reranker()

        if self.column_texts:
            logger.debug("Indexing BM25 columns...")
            self.bm25_columns = BM25()
            self.bm25_columns.index(self.column_texts)

            logger.debug("Indexing ChromaDB columns...")
            self.vector.index_columns(self.column_texts)
        else:
            self.bm25_columns = BM25()

        all_terms = self._build_term_vocabulary()
        self.preprocessor = QueryPreprocessor(all_terms, self.glossary, _VALUE_CORRECTIONS_LOWER)
        self._build_keyword_index()
        self.domain_detector = DomainDetector(self.domains, self.tables, self.vector.encoder)
        if self.domain_detector.centroid_count:
            logger.debug("Built %d domain centroids", self.domain_detector.centroid_count)

        self.db_connected = False
        if DB_SERVER and DB_NAME:
            import pyodbc
            try:
                if DB_USE_WINDOWS_AUTH:
                    cs = f"DRIVER={{ODBC Driver 17 for SQL Server}};SERVER={DB_SERVER};DATABASE={DB_NAME};Trusted_Connection=yes;TrustServerCertificate=yes;"
                else:
                    cs = f"DRIVER={{ODBC Driver 17 for SQL Server}};SERVER={DB_SERVER};DATABASE={DB_NAME};UID={DB_USER};PWD={DB_PASS};TrustServerCertificate=yes;"
                conn = None
                try:
                    conn = pyodbc.connect(cs, timeout=10)
                    cursor = conn.cursor()
                    cursor.execute("SELECT COUNT(*) FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_SCHEMA = ? AND TABLE_TYPE = 'BASE TABLE'", DB_SCHEMA)
                    row = cursor.fetchone()
                    live_count = row[0] if row else 0
                    kb_count = len(self.tables)
                    if live_count != kb_count:
                        logger.warning("KB has %d tables, live DB has %d", kb_count, live_count)
                    else:
                        logger.info("Live DB OK (%d tables match)", live_count)
                    self.db_connected = True
                finally:
                    if conn is not None:
                        conn.close()
            except Exception as e:
                logger.warning("Live DB: %s", e)

    def _build_term_vocabulary(self) -> set[str]:
        terms: set[str] = set()
        for t in self.tables.values():
            for w in t.get("text", "").lower().split():
                cw = re.sub(r"[^a-z0-9]", "", w)
                if len(cw) >= 3:
                    terms.add(cw)
            terms.add(re.sub(r"[^a-z0-9]", "", t["name"].lower()))
            for kw in t.get("all_search_terms", []):
                terms.add(re.sub(r"[^a-z0-9]", "", kw.lower()))
            for intent in t.get("common_user_intents", []):
                for w in intent.lower().split():
                    cw = re.sub(r"[^a-z0-9]", "", w)
                    if len(cw) >= 3:
                        terms.add(cw)

        for col_key, col_text in self.column_texts.items():
            for w in col_text.lower().split():
                cw = re.sub(r"[^a-z0-9]", "", w)
                if len(cw) >= 3:
                    terms.add(cw)
            terms.add(col_key.lower())
            if "." in col_key:
                col_name = col_key.split(".", 1)[1]
                terms.add(re.sub(r"[^a-z0-9]", "", col_name))

        for t in self.tables.values():
            for c in t.get("columns", []):
                for val in c.get("sample_values", []):
                    for w in str(val).lower().split():
                        cw = re.sub(r"[^a-z0-9]", "", w)
                        if len(cw) >= 3:
                            terms.add(cw)

        for dn, dd in self.domains.items():
            terms.add(dn.lower())
            for w in dd.get("description", "").lower().split():
                cw = re.sub(r"[^a-z0-9]", "", w)
                if len(cw) >= 3:
                    terms.add(cw)
            for kw in dd.get("trigger", []):
                terms.add(re.sub(r"[^a-z0-9]", "", kw.lower()))

        for term in self.glossary:
            terms.add(re.sub(r"[^a-z0-9]", "", term.lower()))
            syns = self.glossary[term]
            if isinstance(syns, dict):
                for s in syns.get("synonyms", []):
                    terms.add(re.sub(r"[^a-z0-9]", "", s.lower()))
        return terms

    def _build_keyword_index(self):
        self.keyword_processor = KeywordProcessor(case_sensitive=False)
        self.keyword_to_tables : dict[str, set[str]] ={}

        for name, tbl in self.tables.items():
            kws = {k.lower() for k in tbl.get("all_search_terms", []) if len(k) > 2}
            for c in tbl.get("columns", []):
                for v in c.get("sample_values", []):
                    sv = str(v).lower()
                    if len(sv) > 2:
                        kws.add(sv)
                for alias in c.get("aliases", []):
                    al = alias.lower()
                    if len(al) > 2:
                        kws.add(al)
            for kw in kws:
                self.keyword_to_tables.setdefault(kw, set()).add(name)

        for kw in self.keyword_to_tables:
            self.keyword_processor.add_keyword(kw)

        logger.debug(
            "Indexed %d unique keywords across %d tables (flashtext2)",
            len(self.keyword_to_tables), len(self.tables)
        )


    @staticmethod
    def _is_relevant(domain_hit: bool, keyword_hit: bool, top_score: float) -> bool:
        return domain_hit or keyword_hit or top_score >= 0.3

    def search(self, query: str) -> dict:
        t0 = time.perf_counter()

        intent_info = detect_intent(query)
        search_query = intent_info.get("entity", query)

        expanded = self.preprocessor.expand_query(search_query)
        value_corrected = self.preprocessor.correct_values(expanded)
        corrected = self.preprocessor.correct_typos(value_corrected)

        qn = QueryPreprocessor.normalize_query(corrected)
        ql = corrected

        query_vec = self.vector.encoder.encode([corrected], batch_size=8)["dense_vecs"][0]

        domains = self.domain_detector.detect(corrected, query_vec)
        query_type = self.preprocessor.classify_query(qn, domains)

        if query_type == "ambiguous":
            k = 5
        else:
            k = 3
        join_intent_words = {"name", "with", "and", "uom", "warehouse", "product"}
        if query_type == "multi_table" and len(set(ql.split()) & join_intent_words) >= 2:
            k = max(k, 5) 

        candidate_pool = max(k * CANDIDATE_POOL_MULTIPLIER, CANDIDATE_POOL_MIN)
        rrf_k = max(k * RRF_K_MULTIPLIER, RRF_K_MIN)
        reranker_k = max(k * RERANKER_K_MULTIPLIER, RERANKER_K_MIN)
        
        bm = self.bm25.search(qn, candidate_pool)
        vc = self.vector.search_tables(top_k=TOP_K, query_vec=query_vec)

        rrf = {}
        for rank, (name, _) in enumerate(bm):
            rrf[name] = rrf.get(name, 0) + 1 / (RRF_K + rank + 1)
        for rank, (name, _) in enumerate(vc):
            rrf[name] = rrf.get(name, 0) + 1 / (RRF_K + rank + 1)

        max_rrf = max(rrf.values()) if rrf else 0.50
        q_words_domain = {w for w in ql.lower().split() if w not in STOPWORDS}
        for dn in domains:
            dm = self.domains.get(dn, {})
            for t in dm.get("primary", []) + dm.get("support", []):
                is_already_in_rrf = t in rrf
                tbl_data = self.tables.get(t, {})
                tbl_kws = set(k.lower() for k in tbl_data.get("all_search_terms", []) if len(k) > 2)
                tbl_name_parts = set(t.lower().replace("tbl_", "").replace("_", " ").split())
                sample_vals = set()
                for c in tbl_data.get("columns", []):
                    for v in c.get("sample_values", []):
                        sv = str(v).lower()
                        sample_vals.add(sv)
                        for word in sv.replace("_", " ").split():
                            if len(word) > 2:
                                sample_vals.add(word)
                has_overlap = bool(
                    tbl_kws & q_words_domain
                    or {kw + "s" for kw in tbl_kws} & q_words_domain
                    or {kw[:-1] for kw in tbl_kws if kw.endswith("s") and len(kw) > 3} & q_words_domain
                    or tbl_name_parts & q_words_domain
                    or {np + "s" for np in tbl_name_parts} & q_words_domain
                    or sample_vals & q_words_domain
                )
                if not has_overlap:
                    continue
                if is_already_in_rrf:
                    rrf[t] = max(rrf[t], max_rrf * DOMAIN_BOOST_FACTOR, DOMAIN_BOOST_FLOOR)
                else:
                    rrf[t] = max(max_rrf * DOMAIN_BOOST_FACTOR, DOMAIN_BOOST_FLOOR)

        search_weights = {
            name: tbl.get("search_weight", 5) / 5
            for name, tbl in ((n, self.tables.get(n, {})) for n in rrf)
        }

        qw = {w for w in ql.split() if w not in STOPWORDS}

        matched_phrases = set(self.keyword_processor.extract_keywords(ql.lower()))

        keyword_hit = False
        keyword_scores = {}
        for name, tbl in self.tables.items():
            kws = [k.lower() for k in tbl.get("all_search_terms", []) if len(k) > 2]
            sample_vals = set()
            for c in tbl.get("columns", []):
                for v in c.get("sample_values", []):
                    sv = str(v).lower()
                    if len(sv) > 2:
                        sample_vals.add(sv)
            for sv in sample_vals:
                if sv in ql.lower():
                    kws.append(sv)

            matched_words = set()
            for kw in kws:
                if kw in matched_phrases:               
                    matched_words.add(kw)
                else:
                    kw_words = [w for w in kw.split() if len(w) > 2]
                    if len(kw_words) >= 2 and all(w in qw for w in kw_words):
                        matched_words.add("__multi__" + kw)
                    for w in kw_words:
                        if w in GENERIC_COLUMN_NAMES:
                            continue
                        if w in qw:
                            matched_words.add(w)
                        elif any(wq.startswith(w) or w.startswith(wq) for wq in qw if len(wq) >= 3):
                            matched_words.add(w)
            if matched_words:
                keyword_scores[name] = len(matched_words)
                keyword_hit = True

        for name, mcount in keyword_scores.items():
            boost = KEYWORD_SCORE_PER_MATCH * mcount
            if name in rrf:
                rrf[name] += boost
            else:
                rrf[name] = boost + KEYWORD_NULL_TABLE_BASE

        detected_entities = self.entity_value_extractor.detect_entities(query)
        resolved = self.entity_value_extractor.resolve_locked_tables(detected_entities)
        locked_tables = resolved["locked"]
        suppress_tables = resolved["suppress"]

        if locked_tables:
            for master in locked_tables:
                current = rrf.get(master, 0)
                rrf[master] = max(current, (max(rrf.values()) if rrf else 1.0) * 1.1)
            for sibling in suppress_tables:
                rrf.pop(sibling, None)

        detected_filters = extract_value_filters(query)

        candidates = sorted(rrf.items(), key=lambda x: (-x[1], -search_weights.get(x[0], 1.0)))[:rrf_k]

        top_score = candidates[0][1] if candidates else 0
        domain_hit = bool(domains)
        relevant = self._is_relevant(domain_hit, keyword_hit, top_score)

        if not relevant:
            return {
                "query": query,
                "intent": intent_info,
                "normalized": qn,
                "domains": domains,
                "has_context": False,
                "message": "I don't have relevant context to answer this question.",
                "results": [],
                "joins": [],
                "summary_columns": [],
                "table_count": 0,
                "detected_entities": [],
                "detected_filters": [],
                "_debug": "",
                "latency_ms": round((time.perf_counter() - t0) * 1000, 1),
                "confidence": 0.0,
            }

        try:
            reranked = self.reranker.rerank(
                query, candidates, rrf, self.tables, reranker_k
            )
        except Exception as e:
            logger.warning("Reranker failed (%s), falling back to BM25-only results", e)
            reranked = [
                (name, min(1.0, rrf.get(name, 0) / max(rrf.values(), default=1.0)))
                for name, _ in candidates[:reranker_k]
            ]

        max_rrf_val = max(rrf.values()) if rrf else 1.0
        reranked = [
            (name, round(CE_WEIGHT * score + RRF_WEIGHT * min(1.0, rrf.get(name, 0) / max_rrf_val), 4))
            for name, score in reranked
        ]
        reranked.sort(key=lambda x: (-x[1], -search_weights.get(x[0], 1.0)))
        confidence = reranked[0][1] if reranked else 0.0

        if confidence < 0.05 and not keyword_hit:
            return {
                "query": query,
                "intent": intent_info,
                "normalized": qn,
                "domains": domains,
                "has_context": False,
                "message": "I'm not confident enough to answer this. Can you rephrase or add more detail?",
                "results": [],
                "joins": [],
                "summary_columns": [],
                "table_count": 0,
                "detected_entities": [],
                "detected_filters": [],
                "_debug": "",
                "latency_ms": round((time.perf_counter() - t0) * 1000, 1),
                "confidence": confidence,
            }

        if query_type == "simple_agg" and len(reranked) >= 2 and reranked[0][1] > 0:
            gap = reranked[1][1] / reranked[0][1]
            if gap < SCORE_GAP_FACTOR:
                reranked = reranked[:1]

        col_lookup: dict[str, list[str]] = {}
        if self.column_texts:
            candidate_tables = [r[0] for r in reranked]
            column_results = self._retrieve_columns(corrected, candidate_tables, query_vec=query_vec)
            for col_key, _ in column_results:
                parts = col_key.split(".", 1)
                if len(parts) == 2:
                    tbl, col = parts
                    col_lookup.setdefault(tbl, []).append(col)

        col_cap = 3 if query_type == "simple_agg" else 10
        results = []
        for name, score in reranked:
            effective_threshold = KEYWORD_SCORE_THRESHOLD if (keyword_hit and name in keyword_scores) else SCORE_THRESHOLD
            if score < effective_threshold:
                continue
            if len(results) >= k:
                break
            t = self.tables.get(name, {})
            cols = col_lookup.get(name) or self._match_columns(query, name, t.get("columns", []))
            if not cols:
                cols = [c["name"] for c in t.get("columns", [])[:3]]
            important = t.get("important_columns", [])
            metrics = t.get("business_metrics", [])
            valid_table_col_names = {c["name"] for c in t.get("columns", [])}
            priority_cols = [cname for cname in dict.fromkeys(important + metrics) if cname in valid_table_col_names]
            for cname in priority_cols:
                if cname in cols:
                    cols.remove(cname)
                cols.insert(0, cname)

            q_words = {w.lower() for w in query.split() if len(w) > 2}
            boosted = []
            for cn in list(cols[len(priority_cols):]):
                ci = next((c for c in t.get("columns", []) if c["name"] == cn), None)
                if not ci:
                    continue
                svals = [str(v).lower() for v in ci.get("sample_values", []) if len(str(v)) > 2]
                checks = [cn.lower()] + [a.lower() for a in ci.get("aliases", [])] + [kw.lower() for kw in ci.get("search_keywords", [])] + svals
                if any(any(qw in chk or chk in qw for qw in q_words) for chk in checks if chk):
                    cols.remove(cn)
                    boosted.append(cn)
            ipos = min(len(priority_cols), len(cols))
            for i, cn in enumerate(boosted):
                cols.insert(ipos + i, cn)

            table_joins = [
                j for j in self.joins
                if j["from"] == name or j["to"] == name
            ][:3]

            matching_rules = []
            for rule in self.rules:
                affected = rule.get("tables", [])
                if name in affected:
                    matching_rules.append(rule.get("description", ""))

            for de in detected_entities:
                if de["table"] == name and de["column"] not in cols[:col_cap]:
                    if de["column"] in cols:
                        cols.remove(de["column"])
                        cols.insert(0, de["column"])

            column_samples = {}
            for c in t.get("columns", []):
                vals = c.get("sample_values", [])
                if vals:
                    column_samples[c["name"]] = vals

            results.append({
                "rank": len(results) + 1,
                "table": name,
                "display_name": t.get("display_name", ""),
                "score": score,
                "domain": t.get("domain", ""),
                "description": t.get("description", ""),
                "columns": cols[:col_cap],
                "all_columns": [c["name"] for c in t.get("columns", [])],
                "column_samples": column_samples,
                "common_filters": t.get("common_filters", []),
                "common_groupby": t.get("common_groupby", []),
                "important_columns": [c for c in t.get("important_columns", []) if c in valid_table_col_names],
                "business_metrics": [c for c in t.get("business_metrics", []) if c in valid_table_col_names],
                "suggested_joins": table_joins,
                "matching_rules": matching_rules,
                "primary_key": t.get("primary_key", ""),
                "foreign_keys": t.get("foreign_keys", []),
                "estimated_rows": t.get("estimated_rows", 0),
            })

        result_table_names = {r["table"] for r in results}
        bridge_hits = self.join_graph.find_filter_bridge_tables(query, result_table_names, domains, max_depth=2)
        attr_bridge_hits = self.join_graph.find_attribute_bridge_tables(query, result_table_names)
        bridge_hits = {**bridge_hits, **attr_bridge_hits}
        bridge_tables = sorted(bridge_hits, key=lambda t: (bridge_hits[t], t))[:4]
        for name in bridge_tables:
            t = self.tables.get(name, {})
            if not t:
                continue
            cols = self._match_columns(query, name, t.get("columns", [])) or [c["name"] for c in t.get("columns", [])[:3]]
            column_samples = {}
            for c in t.get("columns", []):
                vals = c.get("sample_values", [])
                if vals:
                    column_samples[c["name"]] = vals
            results.append({
                "rank": len(results) + 1,
                "table": name,
                "display_name": t.get("display_name", ""),
                "score": 0.0,
                "domain": t.get("domain", ""),
                "description": t.get("description", ""),
                "columns": cols[:col_cap],
                "all_columns": [c["name"] for c in t.get("columns", [])],
                "column_samples": column_samples,
                "important_columns": [c for c in t.get("important_columns", []) if c in valid_table_col_names],
                "business_metrics": [c for c in t.get("business_metrics", []) if c in valid_table_col_names],
                "common_filters": t.get("common_filters", []),
                "common_groupby": t.get("common_groupby", []),
                "suggested_joins": [j for j in self.joins if j["from"] == name or j["to"] == name][:3],
                "matching_rules": [],
                "primary_key": t.get("primary_key", ""),
                "foreign_keys": t.get("foreign_keys", []),
                "estimated_rows": t.get("estimated_rows", 0),
                "bridge": True,
            })

        _table_names = {r["table"] for r in results}
        if locked_tables:
            for name in locked_tables:
                if name in result_table_names:
                    continue
                t = self.tables.get(name, {})
                if not t:
                    continue
                cols = self._match_columns(query, name, t.get("columns", [])) or [c["name"] for c in t.get("columns", [])[:3]]
                column_samples = {}
                for c in t.get("columns", []):
                    vals = c.get("sample_values", [])
                    if vals:
                        column_samples[c["name"]] = vals
                results.append({
                    "rank": len(results) + 1,
                    "table": name,
                    "display_name": t.get("display_name", ""),
                    "score": 0.0,
                    "domain": t.get("domain", ""),
                    "description": t.get("description", ""),
                    "columns": cols[:col_cap],
                    "all_columns": [c["name"] for c in t.get("columns", [])],
                    "column_samples": column_samples,
                    "important_columns": [c for c in t.get("important_columns", []) if c in valid_table_col_names],
                    "business_metrics": [c for c in t.get("business_metrics", []) if c in valid_table_col_names],
                    "common_filters": t.get("common_filters", []),
                    "common_groupby": t.get("common_groupby", []),
                    "suggested_joins": [j for j in self.joins if j["from"] == name or j["to"] == name][:3],
                    "matching_rules": [],
                    "primary_key": t.get("primary_key", ""),
                    "foreign_keys": t.get("foreign_keys", []),
                    "estimated_rows": t.get("estimated_rows", 0),
                    "entity_locked": True,
                })

        matched_ops = []
        for kw, label in AGGREGATION_TYPES.items():
            if kw in ql:
                matched_cols = []
                for r in results:
                    for c in r["columns"]:
                        col_info = next(
                            (x for x in self.tables.get(r["table"], {}).get("columns", []) if x["name"] == c),
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

        joins = self.join_graph.match_joins(query, [r["table"] for r in results])
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
            "intent": intent_info,
            "normalized": qn,
            "domains": domains,
            "_reason": reason_str,
            "_debug": debug_str,
            "has_context": True,
            "results": results,
            "joins": joins,
            "summary_columns": all_cols,
            "table_count": len(results),
            "detected_entities": detected_entities,
            "detected_filters": detected_filters,
            "latency_ms": round((time.perf_counter() - t0) * 1000, 1),
            "query_type": query_type,
            "confidence": confidence,
        }
    
    def _retrieve_columns(self, query: str, candidate_tables: list[str], top_k=COLUMN_TOP_K, query_vec=None):
        bm = self.bm25_columns.search(query, top_k * 3)
        vc = self.vector.search_columns(top_k=top_k * 3, query_vec=query_vec)
        candidate_set = set(candidate_tables)
        bm_f = [(k, s) for k, s in bm if k.split(".")[0] in candidate_set]
        vc_f = [(k, s) for k, s in vc if k.split(".")[0] in candidate_set]
        rrf = {}

        for rank, (name, _) in enumerate(bm_f):
            rrf[name] = rrf.get(name, 0) + 1 / (COLUMN_RRF_K + rank + 1)
        for rank, (name, _) in enumerate(vc_f):
            rrf[name] = rrf.get(name, 0) + 1 / (COLUMN_RRF_K + rank + 1)
        candidates = sorted(rrf.items(), key=lambda x: -x[1])[:top_k]

        if not candidates:
            return []
        
        try:
            return self.reranker.rerank_columns(
                query, candidates, self.column_texts, top_k, rrf
            )
        
        except Exception as e:
            logger.warning("Column reranker failed (%s), falling back to RRF-only results", e)
            return candidates[:top_k]

    def _match_columns(self, query: str, table_name: str, columns: list[dict]) -> list[str]:
        ql = query.lower()
        q_words = set(ql.split())

        if QueryPreprocessor.is_simple_count_query(query):
            found = []

            for c in columns:
                name_lower = c["name"].lower()
                if any(kw in name_lower for kw in ["id", "identifier", "name", "status", "code"]):
                    found.append(c["name"])
                if len(found) >= 2:
                    break
            return found or ([columns[0]["name"]] if columns else [])

        scored = []
        for c in columns:
            s = 10 if c["name"].lower() in ql else 0

            display = c.get("display_name", "")
            if display:
                display_parts = [p.strip().lower() for p in display.split("/")]
                if any(p in ql for p in display_parts):
                    s += 8
                elif any(QueryPreprocessor._word_matches_query(w, q_words) for p in display_parts for w in p.split()):
                    s += 5

            desc = c.get("description", "")
            if desc:
                s += sum(3 for w in desc.lower().split() if w in ql)

            aliases = c.get("aliases", [])
            s += sum(5 for a in aliases if a.lower() in ql)
            if any(QueryPreprocessor._word_matches_query(w, q_words) for a in aliases for w in a.lower().split()):
                s += 3

            col_syns = self.col_syns.get(f"{table_name}.{c['name']}", [])
            s += sum(5 for syn in col_syns if syn.lower() in ql)
            if c.get("aggregatable") and any(w in ql for w in ["total", "sum", "avg", "count", "amount", "revenue"]):
                s += 2

            if s > 0:
                scored.append((c, s))

        scored.sort(key=lambda x: -x[1])
        return [c["name"] for c, s in scored if s > 0][:5]
