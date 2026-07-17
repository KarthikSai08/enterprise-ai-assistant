"""
Interactive SQL Metadata Retrieval CLI.

Run:  python -m sql_retrieval

Commands:
  <query>   - search for relevant tables, columns, and join paths
  tables    - list all indexed tables
  help      - show available commands
  exit      - quit
"""

from sql_retrieval.metadata.loader import build
from sql_retrieval.retrieval.engine import Retriever


def print_result(result):
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
        # if x.get("display_name"):
        #     print(f"      {x['display_name']}")

    if result["joins"]:
        print(f"\n  Joins:")
        for j in result["joins"][:5]:
            on = j.get("on", "")
            meaning = j.get("meaning", "")
            print(f"    {on}  ({meaning})" if meaning else f"    {on}")

    cols_fetched = ", ".join(result.get("columns_fetched", [])[:10]) or "-"
    print(f"\n  Tables: {result['table_count']} | Columns: {cols_fetched} | Latency: {result['latency_ms']}ms")


def interactive(retriever):
    print("\nSQL Metadata Retrieval | Type a query | tables | help | exit\n")
    while True:
        try:
            q = input("> ").strip()
        except (EOFError, KeyboardInterrupt):
            break
        if not q or q == "exit":
            break
        if q == "help":
            print(
                "  <query>  - search tables, columns, and joins\n"
                "  tables   - list all indexed tables\n"
                "  exit     - quit"
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
        print_result(result)


def main():
    print("Loading knowledge base ...")
    data = build()
    tables = data["tables"]
    domains = data["domains"]
    joins = data["joins"]
    col_syns = data["col_syns"]
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
