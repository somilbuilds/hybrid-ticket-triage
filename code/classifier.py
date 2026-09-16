from __future__ import annotations

"""General request-type and area helpers for HackerRank ticket triage.

Request-type rules must be written as reusable intent patterns. Do not derive
rules from held-out ticket text in `support_tickets/support_tickets.csv`.
"""

import re
from collections import Counter

from models import EvidenceChunk, Ticket

FEATURE_PATTERNS = [
    re.compile(r"\b(feature request|enhancement|new feature)\b", re.I),
    re.compile(r"\b(would like|want|need|please)\b.{0,60}\b(add|support|allow|enable)\b", re.I),
    re.compile(r"\bsupport for\b", re.I),
]

BUG_PATTERNS = [
    re.compile(r"\b(error|exception|crash|failed|failing|broken|bug)\b", re.I),
    re.compile(r"\b(not working|does not work|can't access|cannot access|stopped working)\b", re.I),
    re.compile(r"\b(down|outage|unavailable|not loading|blank page)\b", re.I),
]

GRATITUDE_OR_GREETING_ONLY = re.compile(
    r"^\s*(hi|hello|hey|thanks|thank you|ok|okay|please help|urgent|help)[\s!,.]*$",
    re.I,
)


def classify_request_type(ticket: Ticket) -> str:
    text = ticket.combined_text.strip()
    if not text or len(text) < 15 or GRATITUDE_OR_GREETING_ONLY.match(text):
        return "invalid"
    if any(pattern.search(text) for pattern in FEATURE_PATTERNS):
        return "feature_request"
    if any(pattern.search(text) for pattern in BUG_PATTERNS):
        return "bug"
    return "product_issue"


def infer_product_area_from_evidence(
    evidence: list[EvidenceChunk],
    request_type: str,
) -> tuple[str, float]:
    if request_type == "invalid":
        return "other", 0.0
    if not evidence:
        return "other", 0.0

    weighted = Counter()
    total = 0.0
    for chunk in evidence:
        weighted[chunk.product_area] += chunk.score
        total += chunk.score
    area, score = weighted.most_common(1)[0]
    probability = score / total if total else 0.0
    return area, probability
