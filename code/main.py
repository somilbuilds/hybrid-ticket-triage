from __future__ import annotations

import argparse
import csv
from pathlib import Path

from dotenv import load_dotenv

from agent import SupportTriageAgent


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Run support triage agent on ticket CSV."
    )
    parser.add_argument(
        "--input",
        default=str(Path("support_tickets") / "support_tickets.csv"),
        help="Input CSV path with Issue/Subject/Company columns.",
    )
    parser.add_argument(
        "--output",
        default=str(Path("support_tickets") / "output.csv"),
        help="Output CSV path to write predictions.",
    )
    parser.add_argument(
        "--data-dir",
        default="data",
        help="Directory containing support corpus subfolders.",
    )
    parser.add_argument(
        "--top-k",
        type=int,
        default=5,
        help="Top evidence chunks to retrieve per ticket.",
    )
    parser.add_argument(
        "--alpha",
        type=float,
        default=0.4,
        help="Lexical weight for hybrid retrieval. Semantic weight is 1-alpha.",
    )
    return parser.parse_args()


def main() -> None:
    load_dotenv()
    args = parse_args()

    agent = SupportTriageAgent(
        data_dir=Path(args.data_dir),
        top_k=args.top_k,
        alpha=args.alpha,
    )

    print(f"Starting recommendation run on {args.input}...", flush=True)
    predictions = agent.run_file(Path(args.input), progress=True)

    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with output_path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=[
                "status",
                "product_area",
                "response",
                "justification",
                "request_type",
            ],
        )
        writer.writeheader()
        for prediction in predictions:
            writer.writerow(prediction.to_row())

    if agent.last_run_interrupted:
        print(
            f"Interrupted by user. Saved {len(predictions)} partial predictions to {output_path}",
            flush=True,
        )
    else:
        print(f"Wrote {len(predictions)} predictions to {output_path}", flush=True)


if __name__ == "__main__":
    main()
