"""Evals — does retrieval actually surface the right products?

For each test query we know which product(s) SHOULD be retrieved. We run the
real hybrid_retrieve() and measure:
  - hit@k       : did at least one expected product appear in the top-k?
  - recall@k    : fraction of expected products that appeared
  - precision@k : fraction of retrieved products that were expected

Run from the backend/ folder (needs MongoDB seeded + ingest done):
    python evals/run_evals.py
"""
import json
import sys
from pathlib import Path

# Allow importing rag.py from the parent (backend/) directory.
sys.path.append(str(Path(__file__).resolve().parent.parent))

import config  # noqa: E402
import rag      # noqa: E402

CASES = json.loads((Path(__file__).parent / "eval_cases.json").read_text(encoding="utf-8"))


def run() -> None:
    k = config.TOP_K
    hits = recalls = precisions = 0.0

    print(f"\nRunning {len(CASES)} eval cases (top-{k} hybrid retrieval)\n")
    print(f"{'hit':>4} {'recall':>7} {'prec':>6}  query")
    print("-" * 70)

    for case in CASES:
        retrieved = rag.hybrid_retrieve(case["query"], k=k)
        expected = set(case["expected"])
        got = set(retrieved)

        overlap = len(expected & got)
        hit = 1.0 if overlap else 0.0
        recall = overlap / len(expected) if expected else 0.0
        precision = overlap / len(got) if got else 0.0

        hits += hit
        recalls += recall
        precisions += precision
        print(f"{'YES' if hit else 'NO ':>4} {recall:>7.2f} {precision:>6.2f}  {case['query']}")

    n = len(CASES)
    print("-" * 70)
    print(f"hit@{k}:       {hits / n:.2f}")
    print(f"recall@{k}:    {recalls / n:.2f}")
    print(f"precision@{k}: {precisions / n:.2f}\n")


if __name__ == "__main__":
    run()
