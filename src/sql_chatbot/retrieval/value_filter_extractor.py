import re

_COMPARISON_PATTERNS = [
    (re.compile(r"\b(greater than or equal to|at least|minimum of|no less than)\s+(\d+(?:\.\d+)?)", re.I), ">="),
    (re.compile(r"\b(less than or equal to|at most|maximum of|no more than)\s+(\d+(?:\.\d+)?)", re.I), "<="),
    (re.compile(r"\b(greater than|more than|above|over|exceeding|exceeds)\s+(\d+(?:\.\d+)?)", re.I), ">"),
    (re.compile(r"\b(less than|under|below)\s+(\d+(?:\.\d+)?)", re.I), "<"),
    (re.compile(r"\b(equal to|exactly|equals)\s+(\d+(?:\.\d+)?)", re.I), "="),
]

_BETWEEN_RE = re.compile(r"\bbetween\s+(\d+(?:\.\d+)?)\s+and\s+(\d+(?:\.\d+)?)", re.I)

_RELATIVE_DATE_PATTERNS = [
    (re.compile(r"\btoday\b", re.I), "today"),
    (re.compile(r"\byesterday\b", re.I), "yesterday"),
    (re.compile(r"\bthis\s+week\b", re.I), "this_week"),
    (re.compile(r"\bthis\s+month\b", re.I), "this_month"),
    (re.compile(r"\bthis\s+quarter\b", re.I), "this_quarter"),
    (re.compile(r"\bthis\s+year\b", re.I), "this_year"),
    (re.compile(r"\blast\s+(\d+)\s+days?\b", re.I), "last_n_days"),
    (re.compile(r"\blast\s+week\b", re.I), "last_week"),
    (re.compile(r"\blast\s+month\b", re.I), "last_month"),
    (re.compile(r"\blast\s+quarter\b", re.I), "last_quarter"),
    (re.compile(r"\blast\s+year\b", re.I), "last_year"),
]

def extract_value_filters(query: str) -> list[dict]:
    filters : list[dict] = []
    m = _BETWEEN_RE.search(query)
    if m:
        raw_low, raw_high = m.group(1), m.group(2)
        if re.fullmatch(r"\d+(?:\.\d+)?", raw_low) and re.fullmatch(r"\d+(?:\.\d+)?", raw_high):
            filters.append({
                "type": "numeric_range", "low": float(raw_low), "high": float(raw_high),
                "raw": m.group(0)
            })

    for pattern, operator in _COMPARISON_PATTERNS:
        m = pattern.search(query)
        if m:
            raw_val = m.group(2)
            if re.fullmatch(r"\d+(?:\.\d+)?", raw_val):
                filters.append({"type": "numeric", "operator": operator, "value": float(raw_val), "raw": m.group(0)})
            break

    for pattern, label in _RELATIVE_DATE_PATTERNS:
        m = pattern.search(query)
        if m:
            entry = {"type": "date", "label": label, "raw": m.group(0)}
            if label == "last_n_days":
                entry["n"] = int(m.group(1))
            filters.append(entry)
            break
    return filters