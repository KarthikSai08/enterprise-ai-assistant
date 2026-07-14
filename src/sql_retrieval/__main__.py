"""
Interactive SQL Metadata Retrieval CLI.

Run:  python -m sql_retrieval

Commands:
  <query>   - search for relevant tables, columns, and join paths
  tables    - list all indexed tables
  help      - show available commands
  exit      - quit
"""

from sql_retrieval.metadata.loader import build, YAML_FILES
from sql_retrieval.retrieval.engine import Retriever


def print_result(result):
    if result.get("relevant") is False:
        print(f"  {result.get('message', 'No relevant context found.')}")
        return

    print(f"\nDomains: {result['domains']}  [{result.get('_reason', '')}]")

    print(f"\n{'Rank':<6}{'Table':<35}{'Score':<10}{'Columns'}")
    print("-" * 80)
    for x in result["results"]:
        cols = ", ".join(x["columns"][:5]) if x["columns"] else "-"
        print(f"  #{x['rank']:<4}{x['table']:<35}{x['score']:<10.4f}{cols}")

    if result["joins"]:
        print("\nJoins:")
        for j in result["joins"][:5]:
            p = j["on"].split("=")
            print(f"  {p[0].strip()}  =  {p[1].strip()}")

    cols_fetched = ", ".join(result.get("columns_fetched", [])[:8]) or "-"
    if len(result.get("columns_fetched", [])) > 8:
        cols_fetched += " ..."

    print(
        f"\n  Tables: {result['table_count']} | "
        f"Columns: {cols_fetched} | "
        f"Latency: {result['latency_ms']}ms"
    )


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
    print("Loading metadata ...")
    tables, domains, joins, col_syns, _ = build()
    ymls = " + ".join(YAML_FILES)
    print(f"  {ymls}")
    print(f"  {len(tables)} tables, {len(domains)} domains, {len(joins)} joins")

    print("Building retriever ...")
    retriever = Retriever(tables, domains, joins, col_syns)

    interactive(retriever)


if __name__ == "__main__":
    main()
