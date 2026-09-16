from __future__ import annotations

import csv
import sys
from dataclasses import replace
from functools import lru_cache
from pathlib import Path
from typing import Any

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

ROOT = Path(__file__).resolve().parent
CODE_DIR = ROOT / "code"
if str(CODE_DIR) not in sys.path:
    sys.path.insert(0, str(CODE_DIR))

from agent import SupportTriageAgent  # noqa: E402
from corpus import CorpusIndex  # noqa: E402
from llm_polish import polish_response  # noqa: E402

load_dotenv(ROOT / ".env")

DATA_DIR = ROOT / "data"
TICKET_CANDIDATES = [
    ROOT / "support_tickets" / "support_tickets" / "support_tickets.csv",
    ROOT / "support_tickets" / "support_tickets.csv",
    ROOT / "support_tickets_github" / "support_tickets.csv",
]
WEB_DIR = ROOT / "web"


class TriageRequest(BaseModel):
    company: str = Field(default="None", max_length=80)
    subject: str = Field(default="", max_length=300)
    issue: str = Field(min_length=3, max_length=5000)


app = FastAPI(title="NLP Support Triage Lab")
app.mount("/static", StaticFiles(directory=WEB_DIR), name="static")


@lru_cache(maxsize=1)
def get_agent() -> SupportTriageAgent:
    return SupportTriageAgent(data_dir=DATA_DIR, top_k=3, alpha=0.4)


def ticket_csv_path() -> Path:
    for path in TICKET_CANDIDATES:
        if path.exists():
            return path
    raise FileNotFoundError("No support ticket CSV found.")


def read_ticket_rows() -> list[dict[str, str]]:
    path = ticket_csv_path()
    with path.open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def summarize(rows: list[dict[str, Any]]) -> dict[str, Any]:
    def counts(key: str) -> dict[str, int]:
        out: dict[str, int] = {}
        for row in rows:
            value = str(row.get(key) or "unknown").strip() or "unknown"
            out[value] = out.get(value, 0) + 1
        return dict(sorted(out.items()))

    return {
        "total": len(rows),
        "status": counts("status"),
        "company": counts("company"),
        "request_type": counts("request_type"),
        "product_area": counts("product_area"),
    }


@app.get("/")
def index() -> FileResponse:
    return FileResponse(WEB_DIR / "index.html")


@app.get("/api/health")
def health() -> dict[str, Any]:
    return {
        "ok": True,
        "data_dir": str(DATA_DIR),
        "ticket_csv": str(ticket_csv_path()),
    }


@app.get("/api/corpus-stats")
def corpus_stats() -> dict[str, Any]:
    index = CorpusIndex(DATA_DIR, use_embeddings=False, use_reranker=False)
    by_area: dict[str, int] = {}
    for doc in index.documents:
        area = str(doc.get("product_area") or "unknown")
        by_area[area] = by_area.get(area, 0) + 1
    return {
        "documents": index.document_count,
        "domain": "hackerrank",
        "product_areas": dict(sorted(by_area.items())),
    }


@app.get("/api/dataset")
def dataset(limit: int = 200) -> dict[str, Any]:
    try:
        rows = read_ticket_rows()
    except FileNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc

    agent = get_agent()
    enriched = []
    for index, row in enumerate(rows[: max(1, min(limit, 500))], start=1):
        details = agent.predict_details(row).to_api()
        prediction = details["prediction"]
        ticket = details["ticket"]
        analysis = details["analysis"]
        enriched.append(
            {
                "id": index,
                "subject": ticket["subject"],
                "issue": ticket["issue"],
                "company": ticket["company"] or analysis["company"],
                "status": prediction["status"],
                "product_area": prediction["product_area"],
                "request_type": prediction["request_type"],
                "confidence": analysis["confidence"],
                "top_score": analysis["top_score"],
                "recommendations": details["recommendations"],
                "justification": prediction["justification"],
            }
        )

    return {
        "source": str(ticket_csv_path()),
        "rows": enriched,
        "summary": summarize(enriched),
    }


@app.post("/api/triage")
def triage(payload: TriageRequest) -> dict[str, Any]:
    row = {
        "Company": payload.company,
        "Subject": payload.subject,
        "Issue": payload.issue,
    }
    details = get_agent().predict_details(row)
    ai_summary = polish_response(
        ticket=details.ticket,
        prediction=details.prediction,
        decision_trace=details.decision_trace,
        evidence=details.evidence,
    )
    if ai_summary:
        details = replace(details, ai_summary=ai_summary)
    return details.to_api()
