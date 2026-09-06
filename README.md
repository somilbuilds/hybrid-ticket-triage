# NLP Support Triage Lab

Local web application for explainable support-ticket triage across HackerRank, Claude, and Visa support domains.

The project began as a CLI hackathon agent. It is now organized as a lab-friendly web app: students can enter support tickets, inspect ranking decisions, view recommended resources, and compare reply/escalation behavior.

## What It Does

- Reads a local markdown support corpus from `data/`.
- Uses hybrid retrieval: lexical TF-IDF/BM25-style scoring plus MiniLM sentence embeddings.
- Re-ranks the top fused candidates with a pretrained cross-encoder.
- Classifies request type: `product_issue`, `feature_request`, `bug`, or `invalid`.
- Routes product area, company, confidence, and reply/escalation status.
- Returns top-3 recommended support resources instead of generating prose answers.
- Displays NLP/ML details in the browser: lexical score, semantic score, rerank score, final score, matched keywords, confidence, and routing reason.
- Keeps new ticket history in browser local storage only. Original CSV datasets are not modified.

## Run The Web App

```bash
pip install -r requirements.txt
uvicorn app:app --reload
```

Open:

```text
http://127.0.0.1:8000
```

## Web Pages

- **Home**: app overview, guidelines, dark/light mode, and main navigation.
- **Check Existing Dataset**: runs recommendation over the existing CSV and shows ticket status, company, product area, request type, confidence, and summary statistics.
- **Enter Your Query**: choose HackerRank, Claude, or Visa; enter a subject and ticket; inspect prediction, recommendations, justification, scores, and model statistics.
- **Session History**: stores manually entered web tickets in local browser storage only.

## Model Approach

This app intentionally avoids training or fine-tuning. The pipeline is:

```text
Ticket text
  -> company and request type rules
  -> lexical retrieval over local markdown corpus
  -> MiniLM sentence-embedding retrieval
  -> score fusion: alpha * lexical + (1-alpha) * semantic
  -> cross-encoder reranking of top fused candidates
  -> evidence-weighted product area routing
  -> escalation rules
  -> top-3 ranked resource recommendations
```

This is laptop-friendly and explainable, which is useful for an NLP lab. The first run downloads pretrained models and caches corpus embeddings in `data/.cache/`; later restarts reuse the cache unless the corpus changes.

## Important Folders

- `app.py`: FastAPI backend.
- `web/`: static frontend.
- `code/`: reusable triage engine.
- `data/`: local support documentation corpus.
- `support_tickets/support_tickets/`: CSV datasets.
- `PROJECT_PLAN.md`: product and implementation plan.
- `AGENT_HANDOFF.md`: concise handoff for future agents.

## CLI Compatibility

The original command-line flow still works:

```bash
python code/main.py --input support_tickets/support_tickets/support_tickets.csv --output support_tickets/support_tickets/output.csv
```
