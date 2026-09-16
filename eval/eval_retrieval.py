from __future__ import annotations

"""Evaluate lexical, semantic, hybrid, and reranked retrieval variants."""

import argparse
import csv
import json
import math
import random
import sys
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
CODE_DIR = ROOT / "code"
if str(CODE_DIR) not in sys.path:
    sys.path.insert(0, str(CODE_DIR))

from corpus import CorpusIndex  # noqa: E402

SEED = 42
ALPHAS = [0.0, 0.2, 0.4, 0.6, 0.8, 1.0]


def load_queries(path: Path) -> list[dict[str, str]]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def heldout_map(rows: list[dict[str, str]]) -> dict[str, list[str]]:
    out: dict[str, list[str]] = {}
    for row in rows:
        out.setdefault(row["gold_path"], []).append(row["heldout_text"])
    return out


def metric_values(ranks: list[int | None]) -> dict[str, list[float]]:
    values = {
        "recall@1": [],
        "recall@3": [],
        "recall@5": [],
        "MRR@10": [],
        "nDCG@10": [],
    }
    for rank in ranks:
        values["recall@1"].append(1.0 if rank is not None and rank <= 1 else 0.0)
        values["recall@3"].append(1.0 if rank is not None and rank <= 3 else 0.0)
        values["recall@5"].append(1.0 if rank is not None and rank <= 5 else 0.0)
        values["MRR@10"].append(0.0 if rank is None or rank > 10 else 1.0 / rank)
        values["nDCG@10"].append(0.0 if rank is None or rank > 10 else 1.0 / math.log2(rank + 1))
    return values


def summarize(name: str, ranks: list[int | None], alpha: float | None = None) -> dict[str, str]:
    values = metric_values(ranks)
    row = {"run": name, "alpha": "" if alpha is None else f"{alpha:.1f}"}
    for metric, scores in values.items():
        arr = np.array(scores, dtype=float)
        row[f"{metric}_mean"] = f"{arr.mean():.4f}"
        row[f"{metric}_std"] = f"{arr.std(ddof=0):.4f}"
    return row


def evaluate(index: CorpusIndex, rows: list[dict[str, str]], mode: str) -> list[int | None]:
    ranks: list[int | None] = []
    for row in rows:
        if mode == "lexical":
            hits = index.lexical_search(row["query"], top_k=10)
        elif mode == "semantic":
            hits = index.semantic_search(row["query"], top_k=10)
        else:
            hits = index.search(row["query"], top_k=10)
        rank = None
        for idx, hit in enumerate(hits, start=1):
            if hit.source_path == row["gold_path"]:
                rank = idx
                break
        ranks.append(rank)
    return ranks


def plot_alpha(results: list[dict[str, str]], out_path: Path) -> None:
    alpha_rows = [row for row in results if row["run"].startswith("hybrid_alpha")]
    xs = [float(row["alpha"]) for row in alpha_rows]
    ys = [float(row["nDCG@10_mean"]) for row in alpha_rows]
    rerank = next((row for row in results if row["run"] == "hybrid_best_rerank"), None)

    plt.figure(figsize=(7, 4.2))
    plt.plot(xs, ys, marker="o", label="Hybrid no rerank")
    if rerank:
        plt.axhline(float(rerank["nDCG@10_mean"]), color="#b42318", linestyle="--", label="Best alpha + rerank")
    plt.xlabel("Lexical weight alpha")
    plt.ylabel("nDCG@10")
    plt.title("Retrieval alpha sweep")
    plt.grid(True, alpha=0.3)
    plt.legend()
    plt.tight_layout()
    plt.savefig(out_path, dpi=150)
    plt.close()


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--queries", default=str(ROOT / "eval" / "datasets" / "retrieval.jsonl"))
    parser.add_argument("--data-dir", default=str(ROOT / "data"))
    parser.add_argument("--limit", type=int, default=0)
    args = parser.parse_args()

    random.seed(SEED)
    np.random.seed(SEED)

    rows = load_queries(Path(args.queries))
    if args.limit:
        rows = rows[: args.limit]
    heldouts = heldout_map(rows)
    result_dir = ROOT / "eval" / "results"
    result_dir.mkdir(parents=True, exist_ok=True)

    results: list[dict[str, str]] = []
    lexical_index = CorpusIndex(Path(args.data_dir), use_embeddings=False, use_reranker=False, heldout_text_by_path=heldouts)
    results.append(summarize("lexical_only", evaluate(lexical_index, rows, "lexical")))

    hybrid_index = CorpusIndex(Path(args.data_dir), alpha=0.0, use_embeddings=True, use_reranker=False, heldout_text_by_path=heldouts)
    results.append(summarize("semantic_only", evaluate(hybrid_index, rows, "semantic")))

    alpha_scores: list[tuple[float, float]] = []
    for alpha in ALPHAS:
        hybrid_index.set_alpha(alpha)
        ranks = evaluate(hybrid_index, rows, "hybrid")
        row = summarize(f"hybrid_alpha_{alpha:.1f}", ranks, alpha=alpha)
        results.append(row)
        alpha_scores.append((alpha, float(row["nDCG@10_mean"])))

    best_alpha = max(alpha_scores, key=lambda item: item[1])[0]
    hybrid_index.set_alpha(best_alpha)
    hybrid_index._use_reranker = True
    results.append(summarize("hybrid_best_rerank", evaluate(hybrid_index, rows, "hybrid"), alpha=best_alpha))

    out_csv = result_dir / "retrieval.csv"
    fieldnames = list(results[0].keys())
    with out_csv.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(results)
    plot_alpha(results, result_dir / "retrieval_alpha_sweep.png")
    print(f"Wrote retrieval metrics to {out_csv}")
    print(f"Wrote alpha sweep plot to {result_dir / 'retrieval_alpha_sweep.png'}")


if __name__ == "__main__":
    main()
