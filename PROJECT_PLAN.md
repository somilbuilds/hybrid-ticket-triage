# Project Plan

## Goal

Complete the migration from a hackathon CLI triage agent into a single-domain HackerRank NLP lab web app. The app should be useful for demonstrating retrieval, ranking, classification, escalation, and explainability on a laptop.

## Current Architecture

- Active domain: HackerRank only.
- Active corpus: `data/hackerrank/`.
- Archived corpora: `data_archive/claude/` and `data_archive/visa/`.
- Backend: FastAPI in `app.py`.
- Frontend: static files in `web/`.
- Engine: Python modules in `code/`.

## Retrieval And Response

- `code/corpus.py` builds a transparent in-memory index.
- Lexical retrieval uses TF-IDF cosine scoring.
- Semantic retrieval uses `sentence-transformers/all-MiniLM-L6-v2`.
- Final fused score uses `alpha * lexical_norm + (1 - alpha) * semantic`.
- Top fused candidates are reranked with `cross-encoder/ms-marco-MiniLM-L-6-v2`.
- Output is ranked recommendations, not generated support prose.
- `code/explain.py` creates an extractive response by selecting source-document sentences from the top recommendation.

## Classification And Routing

- Request type comes from rules in `code/classifier.py`.
- Product area comes from `models/area_clf.joblib` through `code/area_model.py`, with evidence fallback.
- Routing in `code/router.py` escalates on low retrieval score, ambiguous top results, risk terms, privileged/manual actions, and critical outage signals.
- Decision trace is returned through the API for the lab UI.

## Web Requirements

- Home page with app name, basic guidance, light/dark mode, and two actions.
- Dataset board with existing ticket predictions and summary stats.
- New-ticket form for HackerRank support tickets.
- Result panel with status, product area, request type, confidence, extractive response, top-3 resources, scores, matched keywords, and decision trace.
- Session history in local storage only.

## Evaluation

- `eval/build_datasets.py` builds retrieval and classification datasets from the HackerRank corpus.
- `eval/eval_classifier.py` compares keyword rules, TF-IDF logistic regression, and MiniLM logistic regression, then persists the best trainable classifier.
- `eval/eval_retrieval.py` compares lexical, semantic, hybrid alpha sweep, and reranked retrieval.
- Keep retrieval eval CPU-friendly; use `--limit 20` for quick smoke runs and omit the limit for full runs.

## Cleanup Policy

- Do not restore old hackathon `AGENTS.md`, logging workflows, or onboarding files.
- Do not mutate original CSV datasets when users submit web tickets.
- Keep pretrained model caches out of git; commit source code, docs, eval scripts/results, archived corpus moves, and the small persisted classifier.

Groq (`openai/gpt-oss-120b`) is used as an optional, strictly additive response-polish layer -- see `code/llm_polish.py`. It never influences retrieval, classification, or escalation decisions.
