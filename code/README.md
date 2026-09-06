# Triage Engine

This folder contains the reusable Python engine used by the web app and the original CLI.

## Modules

- `agent.py`: orchestrates the full prediction flow.
- `models.py`: dataclasses for tickets, evidence, predictions, and detailed API output.
- `corpus.py`: builds lexical scores, sentence embeddings, fused retrieval scores, and cross-encoder reranking from markdown files under `data/`.
- `classifier.py`: deterministic company, request type, and product area rules.
- `router.py`: reply/escalation policy.
- `main.py`: CLI runner.

## Main API

Use `SupportTriageAgent.predict_details(row)` for the web UI. It returns the normal prediction plus ranked recommendations, lexical/semantic/rerank scores, matched keywords, confidence, and routing metadata.

Use `SupportTriageAgent.predict_row(row)` when only the evaluator-style output fields are needed.

## Training Note

There is no model training in this version. The retriever uses pretrained `all-MiniLM-L6-v2` embeddings and `cross-encoder/ms-marco-MiniLM-L-6-v2` for inference only. Corpus embeddings are cached in `data/.cache/` so startup is faster after the first index build.
