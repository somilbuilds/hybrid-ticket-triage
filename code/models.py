from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True)
class Ticket:
    issue: str
    subject: str
    company: str

    @property
    def combined_text(self) -> str:
        return f"{self.subject}\n{self.issue}".strip()


@dataclass(frozen=True)
class EvidenceChunk:
    company: str
    product_area: str
    source_path: str
    title: str
    content: str
    score: float
    lexical_score: float = 0.0
    semantic_score: float = 0.0
    rerank_score: float = 0.0
    matched_keywords: list[str] = field(default_factory=list)
    match_explanation: str = ""
    lexical_attribution: dict[str, float] = field(default_factory=dict)


@dataclass(frozen=True)
class Prediction:
    status: str
    product_area: str
    response: str
    justification: str
    request_type: str

    def to_row(self) -> dict[str, str]:
        recommendation_text = self.response
        return {
            "status": self.status,
            "product_area": self.product_area,
            "response": recommendation_text,
            "justification": self.justification,
            "request_type": self.request_type,
        }


@dataclass(frozen=True)
class TriageDetails:
    ticket: Ticket
    prediction: Prediction
    company: str
    fallback_company: str
    queries: list[str]
    evidence: list[EvidenceChunk]
    confidence: str
    area_confidence: str
    escalation_reason: str
    decision_trace: dict = field(default_factory=dict)

    def to_api(self) -> dict:
        scores = [chunk.score for chunk in self.evidence]
        return {
            "ticket": {
                "subject": self.ticket.subject,
                "issue": self.ticket.issue,
                "company": self.ticket.company,
            },
            "prediction": self.prediction.to_row(),
            "analysis": {
                "company": self.company,
                "fallback_company": self.fallback_company,
                "queries": self.queries,
                "confidence": self.confidence,
                "area_confidence": self.area_confidence,
                "escalation_reason": self.escalation_reason,
                "top_score": round(scores[0], 4) if scores else 0,
                "average_score": round(sum(scores) / len(scores), 4) if scores else 0,
                "evidence_count": len(self.evidence),
                "decision_trace": self.decision_trace,
            },
            "recommendations": [
                {
                    "rank": index,
                    "company": chunk.company,
                    "product_area": chunk.product_area,
                    "source_path": chunk.source_path,
                    "title": chunk.title,
                    "content": chunk.content,
                    "score": round(chunk.score, 4),
                    "lexical_score": round(chunk.lexical_score, 4),
                    "semantic_score": round(chunk.semantic_score, 4),
                    "rerank_score": round(chunk.rerank_score, 4),
                    "matched_keywords": chunk.matched_keywords,
                    "match_explanation": chunk.match_explanation,
                    "lexical_attribution": chunk.lexical_attribution,
                }
                for index, chunk in enumerate(self.evidence[:3], start=1)
            ],
            "evidence": [
                {
                    "rank": index,
                    "company": chunk.company,
                    "product_area": chunk.product_area,
                    "source_path": chunk.source_path,
                    "title": chunk.title,
                    "content": chunk.content,
                    "score": round(chunk.score, 4),
                    "lexical_score": round(chunk.lexical_score, 4),
                    "semantic_score": round(chunk.semantic_score, 4),
                    "rerank_score": round(chunk.rerank_score, 4),
                    "matched_keywords": chunk.matched_keywords,
                    "match_explanation": chunk.match_explanation,
                    "lexical_attribution": chunk.lexical_attribution,
                }
                for index, chunk in enumerate(self.evidence, start=1)
            ],
        }
