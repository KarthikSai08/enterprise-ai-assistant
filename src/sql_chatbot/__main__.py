from sql_chatbot.config import LLM_PROVIDER, GROQ_API_KEY
from sql_chatbot.metadata.loader import build
from sql_chatbot.retrieval.engine import Retriever
from sql_chatbot.generation.pipeline import run_sql_with_answer


def _llm_available() -> bool:
    if LLM_PROVIDER == "groq":
        return bool(GROQ_API_KEY)
    return True


def print_result(result, retriever=None):
    if result.get("relevant") is False:
        print(f"  {result.get('message', 'No relevant context found.')}")
        return

    domains = result.get("domains", [])
    domain_str = ", ".join(domains) if domains else "none"
    print(f"\nDomains: {domain_str}")

    print(f"\n  {'#':<4}{'Table':<30}{'Score':<8}{'Domain':<12}{'Columns'}")
    print("  " + "-" * 80)
    for x in result["results"]:
        cols = ", ".join(x["columns"][:6]) if x["columns"] else "-"
        print(f"  {x['rank']:<4}{x['table']:<30}{x['score']:<8.4f}{x.get('domain',''):<12}{cols}")

    if result["joins"]:
        print(f"\n  Joins:")
        for j in result["joins"][:5]:
            on = j.get("on", "")
            meaning = j.get("meaning", "")
            print(f"    {on}  ({meaning})" if meaning else f"    {on}")

    cols_fetched = ", ".join(result.get("columns_fetched", [])[:10]) or "-"
    print(f"\n  Tables: {result['table_count']} | Columns: {cols_fetched} | Latency: {result['latency_ms']}ms")

    if result.get("confidence") is not None:
        print(f"  Confidence: {result['confidence']:.4f}")

    if result.get("relevant") and retriever:
        if retriever.db_connected:
            print("\n[Bot] >>> Generating SQL...")
            try:
                corrected_query = result.get("normalized", result["query"])
                sql_result = run_sql_with_answer(corrected_query, result)
                if sql_result.get("not_supported"):
                    msg = sql_result.get("error") or "This question isn't answerable from the database."
                    print(f"  {msg}")
                else:
                    print(f"\n  {'─' * 60}")
                    for line in sql_result["sql"].splitlines():
                        print(f"  {line}")
                    print(f"  {'─' * 60}")
                    if sql_result.get("row_count", 0) > 0:
                        print(f"\n[Bot] >>> Result: {sql_result['row_count']} row(s)")
                        for row in sql_result["rows"][:5]:
                            print(f"        {row}")
                    if sql_result.get("error"):
                        print(f"  Execution error: {sql_result['error']}")
                    if sql_result.get("answer"):
                        print(f"\n[Bot] >>> {sql_result['answer']}")
            except Exception as e:
                print(f"  SQL generation failed: {e}")
        else:
            print("\n  [SQL generation skipped — no live DB connection]")


def interactive(retriever):
    llm_ok = _llm_available()
    print("\nSQL Metadata Retrieval | Type a query | tables | help | exit\n")
    if not llm_ok:
        print("  [LLM not configured — SQL generation disabled]")

    while True:
        try:
            q = input("\n[User] >>> ").strip()
        except (EOFError, KeyboardInterrupt):
            break
        if not q or q == "exit":
            break
        if q == "help":
            print(
                "  <query>   - search tables, columns, and joins\n"
                "  tables    - list all indexed tables\n"
                "  exit      - quit"
            )
            continue
        if q == "tables":
            print(f"\n{'Table':<35}{'Domain':<15}{'Cols':<6}{'Keywords'}")
            print("-" * 70)
            for name, t in sorted(retriever.tables.items()):
                print(
                    f"{name:<35}{t['domain']:<15}"
                    f"{len(t['columns']):<6}{len(t['keywords'])}"
                )
            continue

        result = retriever.search(q)
        print_result(result, retriever)


def main():
    print("Loading knowledge base ...")
    data = build()
    tables = data["tables"]
    domains = data["domains"]
    joins = data["joins"]
    print(f"  {len(tables)} tables, {len(domains)} domains, {len(joins)} joins")
    if data.get("rules"):
        print(f"  {len(data['rules'])} business rules")
    if data.get("examples"):
        print(f"  {len(data['examples'])} example queries")

    print("Building retriever ...")
    retriever = Retriever(data)

    interactive(retriever)


if __name__ == "__main__":
    main()
