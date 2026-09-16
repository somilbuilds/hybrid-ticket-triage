from __future__ import annotations

"""Routing rules for deciding whether a ticket needs human review."""

import re

from corpus import tokenize
from models import EvidenceChunk, Ticket

HIGH_RISK_TERMS = {
    "fraud",
    "identity theft",
    "security vulnerability",
    "critical vulnerability",
    "account takeover",
    "workspace owner",
}

PRIVILEGED_ACTION_PATTERNS = [
    re.compile(r"\b(change|alter|increase|raise|fix|modify|update)\b.{0,50}\b(score|grade|result|outcome)\b", re.I),
    re.compile(r"\b(restore|unlock|grant|remove|delete|ban)\b.{0,50}\b(account|access|user|candidate)\b", re.I),
    re.compile(r"\b(review|override|reevaluate|re-evaluate)\b.{0,50}\b(answer|submission|score|test)\b", re.I),
]


def _confidence_tag(evidence: list[EvidenceChunk]) -> str:
    if not evidence:
        return "low"
    if evidence[0].score >= 0.55:
        return "high"
    if evidence[0].score >= 0.35:
        return "medium"
    return "low"


def assess_routing(
    ticket: Ticket,
    request_type: str,
    evidence: list[EvidenceChunk],
    low_score_threshold: float = 0.30,
    ambiguity_margin: float = 0.03,
) -> tuple[bool, str, str]:
    text = ticket.combined_text.lower()
    confidence = _confidence_tag(evidence)

    if request_type == "invalid":
        return False, "invalid_or_out_of_scope", confidence

    if len(tokenize(ticket.combined_text)) < 3:
        return True, "too_little_issue_detail", confidence

    if any(pattern.search(text) for pattern in PRIVILEGED_ACTION_PATTERNS):
        return True, "manual_or_privileged_action_required", confidence

    if any(term in text for term in HIGH_RISK_TERMS):
        return True, "high_risk_keyword_detected", confidence

    if request_type == "bug" and ("down" in text or "none of" in text):
        return True, "critical_outage_signal", confidence

    if not evidence:
        return True, "no_retrieval_evidence", confidence
    if evidence[0].score < low_score_threshold:
        return True, "low_hybrid_retrieval_score", confidence
    if len(evidence) > 1 and abs(evidence[0].score - evidence[1].score) < ambiguity_margin:
        return True, "ambiguous_top_recommendations", confidence

    return False, "clear_ranked_recommendation", confidence
