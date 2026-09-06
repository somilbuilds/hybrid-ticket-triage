from __future__ import annotations

from models import EvidenceChunk, Ticket
from corpus import tokenize

HIGH_RISK_TERMS = {
    "fraud",
    "identity theft",
    "security vulnerability",
    "critical vulnerability",
    "account takeover",
    "workspace owner",
}

MANDATORY_ESCALATE_TERMS = {
    "increase my score",
    "ban the seller",
    "restore my access immediately",
    "review my answers",
}


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
    is_visa = (ticket.company or "").strip().lower() == "visa" or "visa" in text
    has_lost_card_flow = any(
        term in text
        for term in (
            "lost card",
            "stolen card",
            "traveller",
            "traveler",
            "travel cheque",
            "traveller's cheque",
            "traveler's cheque",
        )
    )
    confidence = _confidence_tag(evidence)

    if request_type == "invalid":
        return False, "invalid_or_out_of_scope", confidence

    if len(tokenize(ticket.combined_text)) < 3:
        return True, "too_little_issue_detail", confidence

    if any(term in text for term in MANDATORY_ESCALATE_TERMS):
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

    if is_visa and has_lost_card_flow:
        return False, "visa_loss_or_travel_flow_supported", confidence

    return False, "clear_ranked_recommendation", confidence
