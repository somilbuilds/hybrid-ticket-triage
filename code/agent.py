from __future__ import annotations

import csv
from pathlib import Path

from classifier import (
    classify_request_type,
    infer_product_area_from_evidence,
)
from corpus import CorpusIndex
from area_model import predict_area
from explain import build_decision_trace, extractive_response
from models import EvidenceChunk, Prediction, Ticket, TriageDetails
from router import assess_routing


class SupportTriageAgent:
    def __init__(self, data_dir: Path, top_k: int = 3, alpha: float = 0.4) -> None:
        self._index = CorpusIndex(data_dir=data_dir, alpha=alpha)
        self._top_k = top_k
        self.last_run_interrupted = False

    def run_file(self, csv_path: Path, progress: bool = False) -> list[Prediction]:
        rows = self._read_rows(csv_path)
        predictions: list[Prediction] = []
        self.last_run_interrupted = False

        total = len(rows)
        for index, row in enumerate(rows, start=1):
            try:
                predictions.append(self.predict_row(row))
                if progress:
                    print(f"Processed {index}/{total}", flush=True)
            except KeyboardInterrupt:
                self.last_run_interrupted = True
                break
        return predictions

    def predict_row(self, row: dict[str, str]) -> Prediction:
        return self.predict_details(row).prediction

    def predict_details(self, row: dict[str, str]) -> TriageDetails:
        ticket = Ticket(
            issue=self._pick(row, "issue", "Issue"),
            subject=self._pick(row, "subject", "Subject"),
            company="HackerRank",
        )
        request_type = classify_request_type(ticket)
        queries = self._build_queries(ticket)

        evidence = self._retrieve_evidence(queries=queries)

        product_area, area_probability = predict_area(ticket.combined_text)
        if area_probability <= 0:
            product_area, area_probability = infer_product_area_from_evidence(
                evidence=evidence,
                request_type=request_type,
            )
        escalated, escalation_reason, confidence = assess_routing(
            ticket=ticket,
            request_type=request_type,
            evidence=evidence,
        )
        status = "escalated" if escalated else "replied"
        response = (
            "Escalate to a human reviewer before replying. The ranked resources remain useful as context."
            if escalated
            else extractive_response(ticket.combined_text, evidence[0] if evidence else None)
        )
        decision_trace = build_decision_trace(
            request_type=request_type,
            product_area=product_area,
            area_probability=area_probability,
            confidence=confidence,
            escalation_reason=escalation_reason,
            evidence=evidence,
        )
        justification = (
            f"{'Escalated' if escalated else 'Recommended resources'} in {product_area} "
            f"because {escalation_reason}; confidence={confidence}; "
            f"area_probability={area_probability:.3f}; top_recommendations={len(evidence)}."
        )

        prediction = Prediction(
            status=status,
            product_area=product_area,
            response=response,
            justification=justification,
            request_type=request_type,
        )

        return TriageDetails(
            ticket=ticket,
            prediction=prediction,
            company="hackerrank",
            fallback_company="hackerrank",
            queries=queries,
            evidence=evidence,
            confidence=confidence,
            area_confidence=f"{area_probability:.3f}",
            escalation_reason=escalation_reason,
            decision_trace=decision_trace,
        )

    def _build_queries(self, ticket: Ticket) -> list[str]:
        text = ticket.combined_text
        separators = ["\n", ". ", " and ", " also ", "; "]
        clauses = [text]
        for sep in separators:
            next_clauses: list[str] = []
            for clause in clauses:
                next_clauses.extend(part.strip() for part in clause.split(sep) if part.strip())
            clauses = next_clauses or clauses
        ranked = sorted(clauses, key=len, reverse=True)
        unique: list[str] = []
        for clause in ranked:
            if clause not in unique:
                unique.append(clause)
            if len(unique) >= 2:
                break
        return unique or [text]

    def _retrieve_evidence(
        self,
        queries: list[str],
    ) -> list[EvidenceChunk]:
        collected: dict[str, EvidenceChunk] = {}

        for query in queries:
            for chunk in self._index.search(query=query, top_k=self._top_k):
                key = chunk.source_path
                prev = collected.get(key)
                if prev is None or chunk.score > prev.score:
                    collected[key] = chunk

        merged = sorted(collected.values(), key=lambda c: c.score, reverse=True)
        return merged[: self._top_k]

    @staticmethod
    def _format_recommendation_summary(evidence: list[EvidenceChunk]) -> str:
        if not evidence:
            return "No reliable support resource recommendation found."
        return " | ".join(
            f"{index}. {chunk.title} ({chunk.source_path})"
            for index, chunk in enumerate(evidence[:3], start=1)
        )

    @staticmethod
    def _read_rows(csv_path: Path) -> list[dict[str, str]]:
        with csv_path.open("r", encoding="utf-8", newline="") as handle:
            reader = csv.DictReader(handle)
            return list(reader)

    @staticmethod
    def _pick(row: dict[str, str], *keys: str) -> str:
        for key in keys:
            value = row.get(key)
            if value is not None:
                return value.strip()
        return ""
