from __future__ import annotations

"""Build deterministic evaluation datasets from the HackerRank corpus.

The retrieval set uses pseudo queries derived from each document title and lead
paragraph. Evaluation code passes these query strings back into `CorpusIndex`
as held-out text for the corresponding gold document, so exact source text is
not indexed for the same query.
"""

import csv
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CODE_DIR = ROOT / "code"
if str(CODE_DIR) not in sys.path:
    sys.path.insert(0, str(CODE_DIR))

from corpus import first_tokens, normalize_product_area  # noqa: E402

DATA_DIR = ROOT / "data" / "hackerrank"
OUT_DIR = ROOT / "eval" / "datasets"


def extract_title(stem: str, text: str) -> str:
    for line in text.splitlines():
        line = line.strip()
        if line.startswith("#"):
            return line.lstrip("#").strip() or stem
    return stem.replace("-", " ")


def clean_content(text: str) -> str:
    if text.startswith("---"):
        parts = text.split("---", 2)
        if len(parts) == 3:
            text = parts[2]
    return "\n".join(line.rstrip() for line in text.splitlines())


def first_paragraph(text: str) -> str:
    for block in text.split("\n\n"):
        lines = [line.strip() for line in block.splitlines()]
        lines = [
            line
            for line in lines
            if line and not line.startswith("#") and not line.startswith("---")
        ]
        if lines:
            return " ".join(lines)
    return ""


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    retrieval_path = OUT_DIR / "retrieval.jsonl"
    classification_path = OUT_DIR / "classification.csv"

    retrieval_rows: list[dict[str, str]] = []
    classification_rows: list[dict[str, str]] = []

    for md_path in sorted(DATA_DIR.rglob("*.md")):
        rel = md_path.relative_to(ROOT / "data")
        parts = rel.parts
        if len(parts) < 3:
            continue
        source_path = str(rel).replace("\\", "/")
        product_area = normalize_product_area(parts[1])
        raw = md_path.read_text(encoding="utf-8", errors="ignore")
        title = extract_title(md_path.stem, raw)
        content = clean_content(raw)
        lead = first_tokens(first_paragraph(content), 30)
        body = first_tokens(content, 200)

        if title:
            retrieval_rows.append(
                {
                    "query_id": f"{source_path}::title",
                    "query_type": "title_query",
                    "query": title,
                    "gold_path": source_path,
                    "heldout_text": title,
                }
            )
        if lead:
            retrieval_rows.append(
                {
                    "query_id": f"{source_path}::lead",
                    "query_type": "lead_query",
                    "query": lead,
                    "gold_path": source_path,
                    "heldout_text": lead,
                }
            )

        classification_rows.append(
            {
                "source_path": source_path,
                "label": product_area,
                "text": f"{title}\n{body}".strip(),
            }
        )

    with retrieval_path.open("w", encoding="utf-8", newline="\n") as handle:
        for row in retrieval_rows:
            handle.write(json.dumps(row, ensure_ascii=True) + "\n")

    with classification_path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=["source_path", "label", "text"])
        writer.writeheader()
        writer.writerows(classification_rows)

    print(f"Wrote {len(retrieval_rows)} retrieval rows to {retrieval_path}")
    print(f"Wrote {len(classification_rows)} classification rows to {classification_path}")


if __name__ == "__main__":
    main()
