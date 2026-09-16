from __future__ import annotations

"""Optional Groq response-polish layer.

This module is deliberately downstream of triage. It never participates in
retrieval, classification, ranking, or escalation decisions.
"""

import logging
import os

from models import EvidenceChunk, Prediction, Ticket

LOGGER = logging.getLogger(__name__)
PRIMARY_MODEL = "openai/gpt-oss-120b"
FALLBACK_MODEL = "openai/gpt-oss-20b"
GROQ_BASE_URL = "https://api.groq.com/openai/v1"


def polish_response(
    ticket: Ticket,
    prediction: Prediction,
    decision_trace: dict,
    evidence: list[EvidenceChunk],
) -> str | None:
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        return None

    try:
        from openai import OpenAI
    except Exception as exc:  # pragma: no cover - depends on local environment
        LOGGER.warning("Groq polish skipped because the OpenAI SDK is unavailable: %s", exc)
        return None

    client = OpenAI(api_key=api_key, base_url=GROQ_BASE_URL, timeout=8.0)
    messages = _build_messages(ticket, prediction, decision_trace, evidence)

    for model in (PRIMARY_MODEL, FALLBACK_MODEL):
        try:
            response = client.chat.completions.create(
                model=model,
                messages=messages,
                temperature=0.2,
                max_tokens=220,
            )
            content = response.choices[0].message.content
            if content:
                return content.strip()
        except Exception as exc:  # pragma: no cover - network/API behavior
            LOGGER.warning("Groq polish failed with %s: %s", model, exc)
    return None


def _build_messages(
    ticket: Ticket,
    prediction: Prediction,
    decision_trace: dict,
    evidence: list[EvidenceChunk],
) -> list[dict[str, str]]:
    evidence_text = "\n\n".join(
        f"Evidence {index}: {chunk.title}\n{chunk.content[:1200]}"
        for index, chunk in enumerate(evidence[:3], start=1)
    )
    escalation_reason = decision_trace.get("routing_reason", "")
    user_content = f"""
Ticket subject:
{ticket.subject}

Ticket issue:
{ticket.issue}

Already-decided status:
{prediction.status}

Already-decided product area:
{prediction.product_area}

Already-decided request type:
{prediction.request_type}

Escalation reason, if any:
{escalation_reason}

Evidence:
{evidence_text}
""".strip()

    return [
        {
            "role": "system",
            "content": (
                "You are a support triage response polish layer. Rephrase and explain the already-decided "
                "triage result in friendly plain language. Do not add facts, steps, or claims not present "
                "in the evidence. Do not change the escalation status, product area, request type, or "
                "decision. Keep the answer to a few sentences."
            ),
        },
        {"role": "user", "content": user_content},
    ]
