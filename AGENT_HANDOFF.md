# Agent Handoff

## User Intent

The user wants the old CLI hackathon support-triage project turned into a polished webpage/GUI for an NLP lab. The current target is no longer three-domain triage. It is a focused HackerRank support-ticket triage app with explainable retrieval and recommendations.

## Do Not Reintroduce

- Old hackathon `AGENTS.md` behavior.
- Logging/onboarding workflows.
- Gemini, Groq, or other LLM prose-polish response generation.
- Claude/Visa as active runtime domains.
- Writes to the original ticket CSVs from the web UI.

## Current System

- Active docs: `data/hackerrank/`.
- Archived docs: `data_archive/claude/`, `data_archive/visa/`.
- FastAPI backend: `app.py`.
- Static UI: `web/index.html`, `web/styles.css`, `web/app.js`.
- Core engine: `code/agent.py`.
- Hybrid retriever: `code/corpus.py`.
- Product-area model loader: `code/area_model.py`.
- Decision/extractive explanation helpers: `code/explain.py`.
- Routing rules: `code/router.py`.
- Dataclasses/API serialization: `code/models.py`.

## Current Pipeline

```text
ticket text
  -> request-type rules
  -> product-area classifier
  -> TF-IDF lexical retrieval
  -> MiniLM semantic retrieval
  -> alpha fusion
  -> cross-encoder rerank
  -> escalation/routing rules
  -> extractive source response + top-3 resource recommendations
```

## Evaluation Commands

```bash
python eval/build_datasets.py
python eval/eval_classifier.py
python eval/eval_retrieval.py --limit 20
```

The full retrieval evaluation can be run by omitting `--limit`, but it is slower on CPU because the cross-encoder reranks many query/resource pairs.

## Expected Run Command

```bash
pip install -r requirements.txt
uvicorn app:app --reload
```

Then open `http://127.0.0.1:8000`.
