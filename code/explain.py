from __future__ import annotations

"""Small explainability helpers for triage decisions.

These functions intentionally avoid prose generation. They select source
sentences from the retrieved support article and expose simple lexical
attribution that is easy to inspect in a lab setting.
"""

import re
from collections import Counter

from corpus import tokenize
from models import EvidenceChunk

SENTENCE_RE = re.compile(r"(?<=[.!?])\s+|\n+")


def split_sentences(text: str) -> list[str]:
    sentences = []
    for part in SENTENCE_RE.split(text):
        clean = " ".join(part.split())
        if len(clean) >= 35:
            sentences.append(clean)
    return sentences


def extractive_response(ticket_text: str, chunk: EvidenceChunk | None, max_sentences: int = 3) -> str:
    if chunk is None:
        return "No reliable support article sentence could be selected."

    query_tokens = Counter(tokenize(ticket_text))
    if not query_tokens:
        return f"See {chunk.title}. Source: {chunk.source_path}"

    scored: list[tuple[float, int, str]] = []
    for index, sentence in enumerate(split_sentences(chunk.content)):
        sentence_tokens = Counter(tokenize(sentence))
        overlap = sum(query_tokens[token] * sentence_tokens.get(token, 0) for token in query_tokens)
        if overlap <= 0:
            continue
        coverage = overlap / max(sum(query_tokens.values()), 1)
        length_penalty = min(len(sentence) / 280.0, 1.4)
        scored.append((coverage / length_penalty, index, sentence))

    if not scored:
        return f"See {chunk.title}. Source: {chunk.source_path}"

    selected = sorted(scored, key=lambda item: item[0], reverse=True)[:max_sentences]
    ordered = [sentence for _, _, sentence in sorted(selected, key=lambda item: item[1])]
    return " ".join(ordered) + f" Source: {chunk.source_path}"


def lexical_trace(chunk: EvidenceChunk | None, limit: int = 6) -> list[dict[str, float]]:
    if chunk is None:
        return []
    return [
        {"token": token, "weight": round(float(weight), 4)}
        for token, weight in sorted(
            chunk.lexical_attribution.items(),
            key=lambda item: item[1],
            reverse=True,
        )[:limit]
    ]


def build_decision_trace(
    *,
    request_type: str,
    product_area: str,
    area_probability: float,
    confidence: str,
    escalation_reason: str,
    evidence: list[EvidenceChunk],
) -> dict:
    top = evidence[0] if evidence else None
    second = evidence[1] if len(evidence) > 1 else None
    return {
        "request_type_rule": request_type,
        "product_area": product_area,
        "area_probability": round(area_probability, 4),
        "confidence": confidence,
        "routing_reason": escalation_reason,
        "top_resource": {
            "title": top.title,
            "path": top.source_path,
            "product_area": top.product_area,
            "final_score": round(top.score, 4),
            "lexical_score": round(top.lexical_score, 4),
            "semantic_score": round(top.semantic_score, 4),
            "rerank_score": round(top.rerank_score, 4),
        }
        if top
        else None,
        "ambiguity_gap": round(abs(top.score - second.score), 4) if top and second else None,
        "top_lexical_attribution": lexical_trace(top),
    }
