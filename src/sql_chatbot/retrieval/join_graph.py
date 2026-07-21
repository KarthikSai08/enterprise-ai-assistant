from collections import deque


class JoinGraph:
    def __init__(self, joins: list[dict], tables: dict):
        self.joins = joins
        self.tables = tables
        self.fk_graph: dict[str, dict[str, dict]] = {}
        for j in joins:
            frm = j["from"]
            to = j["to"]
            edge = {
                "on": j.get("on", ""),
                "join_type": j.get("default_join_type", j.get("join_type", "INNER")),
                "meaning": j.get("meaning", ""),
            }
            self.fk_graph.setdefault(frm, {})[to] = edge
            self.fk_graph.setdefault(to, {})[frm] = edge

    def bfs_path(self, start: str, end: str, max_depth: int) -> list[dict] | None:
        if start == end:
            return []
        visited = {start}
        queue = deque([[start]])
        while queue:
            path = queue.popleft()
            if len(path) - 1 >= max_depth:
                continue
            for neighbor in self.fk_graph.get(path[-1], {}):
                if neighbor == end:
                    full_path = path + [neighbor]
                    return self._path_to_edges(full_path)
                if neighbor not in visited:
                    visited.add(neighbor)
                    queue.append(path + [neighbor])
        return None

    def _path_to_edges(self, path: list[str]) -> list[dict]:
        edges = []
        for i in range(len(path) - 1):
            frm, to = path[i], path[i + 1]
            edge = self.fk_graph.get(frm, {}).get(to, {})
            edges.append({
                "from": frm,
                "to": to,
                "on": edge.get("on", ""),
                "join_type": edge.get("join_type", "INNER"),
                "meaning": edge.get("meaning", ""),
            })
        return edges

    def find_bridge_tables(self, candidate_names: set, max_depth: int = 2) -> set:
        bridges = set()
        names = list(candidate_names)
        for i, a in enumerate(names):
            for b in names[i + 1:]:
                path_edges = self.bfs_path(a, b, max_depth)
                if path_edges:
                    path_tables = set()
                    for edge in path_edges:
                        path_tables.add(edge["from"])
                        path_tables.add(edge["to"])
                    for node in path_tables:
                        if node in candidate_names:
                            bridges.add(node)
        return bridges

    def match_joins(self, query: str, table_names: list[str]) -> list[dict]:
        ql = query.lower()
        ts = set(table_names)

        if self.joins:
            bridge_tables = self.find_bridge_tables(ts, max_depth=2)
            ts_expanded = ts | bridge_tables

            scored_paths = []
            seen = set()
            names_list = list(ts_expanded)
            for i, a in enumerate(names_list):
                for b in names_list[i + 1:]:
                    path_edges = self.bfs_path(a, b, max_depth=2)
                    if not path_edges:
                        continue
                    key = "->".join(e["from"] for e in path_edges) + "->" + path_edges[-1]["to"]
                    if key in seen:
                        continue
                    seen.add(key)
                    meaning_score = sum(
                        3 for e in path_edges for w in e["meaning"].split() if w in ql
                    )
                    scored_paths.append((path_edges, meaning_score))

            scored_paths.sort(key=lambda x: (-x[1], len(x[0])))
            flat = [e for path_edges, _ in scored_paths[:5] for e in path_edges]
            return flat[:5]

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
                            "join_type": "INNER",
                            "meaning": fk.get("name", ""),
                        })
        return inferred[:5]
