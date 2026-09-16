from __future__ import annotations

"""Side-by-side lexical vs hybrid+rerank retrieval sanity check."""

import argparse
import csv
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CODE_DIR = ROOT / "code"
if str(CODE_DIR) not in sys.path:
    sys.path.insert(0, str(CODE_DIR))

from corpus import CorpusIndex  # noqa: E402


def load_rows(path: Path, limit: int) -> list[dict[str, str]]:
    rows = [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]
    return rows[:limit]


def heldout_map(rows: list[dict[str, str]]) -> dict[str, list[str]]:
    out: dict[str, list[str]] = {}
    for row in rows:
        out.setdefault(row["gold_path"], []).append(row["heldout_text"])
    return out


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--queries", default=str(ROOT / "eval" / "datasets" / "retrieval.jsonl"))
    parser.add_argument("--data-dir", default=str(ROOT / "data"))
    parser.add_argument("--limit", type=int, default=10)
    args = parser.parse_args()

    rows = load_rows(Path(args.queries), args.limit)
    heldouts = heldout_map(rows)
    lexical = CorpusIndex(Path(args.data_dir), use_embeddings=False, use_reranker=False, heldout_text_by_path=heldouts)
    hybrid = CorpusIndex(Path(args.data_dir), alpha=0.4, use_embeddings=True, use_reranker=True, heldout_text_by_path=heldouts)

    out_path = ROOT / "eval" / "results" / "retrieval_comparison.csv"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = [
        "query",
        "gold_path",
        "lexical_top_title",
        "lexical_top_path",
        "lexical_score",
        "hybrid_top_title",
        "hybrid_top_path",
        "hybrid_score",
        "hybrid_rerank_score",
        "hybrid_match_explanation",
    ]
    with out_path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            old_hit = (lexical.lexical_search(row["query"], top_k=1) or [None])[0]
            new_hit = (hybrid.search(row["query"], top_k=1) or [None])[0]
            writer.writerow(
                {
                    "query": row["query"],
                    "gold_path": row["gold_path"],
                    "lexical_top_title": old_hit.title if old_hit else "",
                    "lexical_top_path": old_hit.source_path if old_hit else "",
                    "lexical_score": f"{old_hit.score:.4f}" if old_hit else "",
                    "hybrid_top_title": new_hit.title if new_hit else "",
                    "hybrid_top_path": new_hit.source_path if new_hit else "",
                    "hybrid_score": f"{new_hit.score:.4f}" if new_hit else "",
                    "hybrid_rerank_score": f"{new_hit.rerank_score:.4f}" if new_hit else "",
                    "hybrid_match_explanation": new_hit.match_explanation if new_hit else "",
                }
            )
    print(f"Wrote retrieval comparison to {out_path}")


if __name__ == "__main__":
    main()
