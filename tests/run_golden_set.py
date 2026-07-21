"""
Golden set runner for Retriever.search().

Usage:
    python tests/run_golden_set.py [--debug]
"""

import argparse
import logging
import sys
import time
from pathlib import Path

import yaml

# ── Project import (assumes src/ is on path or PYTHONPATH set) ──
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

from sql_chatbot.retrieval.engine import Retriever


def load_golden(path: Path) -> list[dict]:
    with open(path, encoding="utf-8") as f:
        return yaml.safe_load(f)["cases"]


def run() -> int:
    parser = argparse.ArgumentParser(description="Run golden set tests")
    parser.add_argument("--debug", action="store_true", help="Enable DEBUG logging")
    args = parser.parse_args()

    level = logging.DEBUG if args.debug else logging.WARNING
    logging.basicConfig(
        level=level,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        datefmt="%H:%M:%S",
    )
    logger = logging.getLogger("golden")

    golden_path = Path(__file__).resolve().parent / "golden_set.yaml"
    cases = load_golden(golden_path)

    print(f"[golden] Loading {len(cases)} test cases from {golden_path}")
    retriever = Retriever()
    print()

    passed = 0
    failed = 0
    results = []

    for i, case in enumerate(cases, 1):
        query = case["query"]
        expected = case["expected"]
        ctype = case["type"]

        t0 = time.perf_counter()
        out = retriever.search(query)
        elapsed = round((time.perf_counter() - t0) * 1000, 1)

        top_tables = [r["table"] for r in out.get("results", [])]
        is_relevant = out.get("relevant", False)
        reasons = out.get("_reason", "")

        if ctype == "not_supported":
            ok = not is_relevant or len(top_tables) == 0
        elif ctype in ("single", "known_failure"):
            ok = all(e in top_tables for e in expected)
        elif ctype == "cross-domain":
            ok = all(e in top_tables for e in expected)
        else:
            ok = False

        status = "PASS" if ok else "FAIL"
        if ok:
            passed += 1
        else:
            failed += 1

        expected_str = ", ".join(expected) if expected else "<none>"
        top_str = ", ".join(top_tables) if top_tables else "<none>"
        detail = f"  top={top_str}  reason={reasons}  score={out.get('confidence', 0):.3f}"
        if not ok and ctype == "known_failure":
            detail += "  [KNOWN FAILURE — acceptable]"

        results.append((status, ctype, query, expected_str, top_str, elapsed, detail))
        print(f"  [{status}] #{i:2d}  {query}")

    print()
    print(f"{'=' * 72}")
    print("  DETAILED RESULTS:")
    print(f"{'=' * 72}")
    for status, ctype, query, expected_str, top_str, elapsed, detail in results:
        print(f"  [{status}] ({ctype:16s}) {query}")
        print(f"          expect={expected_str}")
        print(detail)
        print()

    print(f"{'=' * 72}")
    print(f"  SUMMARY: {passed} passed, {failed} failed ({len(cases)} total)")
    print(f"{'=' * 72}")

    return 0 if failed == 0 else 1


if __name__ == "__main__":
    sys.exit(run())
