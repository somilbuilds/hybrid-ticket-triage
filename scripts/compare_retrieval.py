from __future__ import annotations

import argparse
import csv
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CODE_DIR = ROOT / "code"
if str(CODE_DIR) not in sys.path:
    sys.path.insert(0, str(CODE_DIR))

from classifier import infer_company  # noqa: E402
from corpus import CorpusIndex  # noqa: E402
from models import Ticket  # noqa: E402


def pick(row: dict[str, str], *keys: str) -> str:
    for key in keys:
        value = row.get(key)
        if value is not None:
            return value.strip()
    return ""


def read_rows(path: Path, limit: int) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))[:limit]


def main() -> None:
    parser = argparse.ArgumentParser(description="Compare lexical-only vs hybrid reranked retrieval.")
    parser.add_argument(
        "--tickets",
        default=str(ROOT / "support_tickets" / "support_tickets" / "sample_support_tickets.csv"),
    )
    parser.add_argument("--data-dir", default=str(ROOT / "data"))
    parser.add_argument("--limit", type=int, default=8)
    parser.add_argument("--alpha", type=float, default=0.4)
    args = parser.parse_args()

    ticket_path = Path(args.tickets)
    data_dir = Path(args.data_dir)

    old_index = CorpusIndex(data_dir=data_dir, use_embeddings=False, use_reranker=False)
    new_index = CorpusIndex(data_dir=data_dir, alpha=args.alpha, use_embeddings=True, use_reranker=True)

    print("ID | Company | Subject | Old TF-IDF top match | New hybrid+rerank top match")
    print("-- | ------- | ------- | ------------------- | ----------------------------")
    for index, row in enumerate(read_rows(ticket_path, args.limit), start=1):
        ticket = Ticket(
            issue=pick(row, "issue", "Issue"),
            subject=pick(row, "subject", "Subject"),
            company=pick(row, "company", "Company"),
        )
        company = infer_company(ticket)
        company_hint = company if company in {"hackerrank", "claude", "visa"} else None
        query = ticket.combined_text
        old = old_index.lexical_search(query=query, top_k=1, company_hint=company_hint)
        new = new_index.search(query=query, top_k=1, company_hint=company_hint)
        old_text = f"{old[0].title} ({old[0].score:.3f})" if old else "no match"
        new_text = f"{new[0].title} ({new[0].score:.3f}; rerank {new[0].rerank_score:.3f})" if new else "no match"
        subject = (ticket.subject or ticket.issue).replace("|", "/")
        print(f"{index} | {ticket.company or company} | {subject[:54]} | {old_text} | {new_text}")


if __name__ == "__main__":
    main()
