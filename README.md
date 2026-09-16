# HackerRank NLP Support Triage Lab

Local web software for explainable HackerRank support-ticket triage. The project started as a CLI hackathon submission; it is now a single-domain, UI-first NLP lab app.

## What It Does

- Reads HackerRank support documentation from `data/hackerrank/`.
- Archives older Claude/Visa corpora under `data_archive/` so they do not affect inference.
- Uses hybrid retrieval: TF-IDF lexical similarity plus MiniLM sentence embeddings.
- Fuses scores with configurable alpha, then re-ranks the top candidates with `cross-encoder/ms-marco-MiniLM-L-6-v2`.
- Returns top-3 recommended resources with title, path, score, matched keywords, and a one-line match reason.
- Produces an extractive source response from the top support article; it does not generate fake LLM prose.
- Classifies request type and product area, then decides `replied` vs `escalated`.
- Shows decision trace details in the browser: confidence, routing reason, score gap, area probability, and lexical token attribution.
- Stores manually submitted ticket history only in browser local storage. Original CSV files are not modified.

## Run

```bash
pip install -r requirements.txt
uvicorn app:app --reload
```

Open:

```text
http://127.0.0.1:8000
```

The first run may download pretrained `sentence-transformers` models. Corpus embeddings are cached in `data/.cache/`, so server restarts do not rebuild embeddings unless the corpus changes.

## Web Views

- **Home**: project name, short guidance, light/dark mode, and two main actions.
- **Check Existing Dataset**: predicts status for the existing ticket CSV and shows domain, product area, request type, confidence, top score, and summary cards.
- **Enter Your Query**: accepts a new HackerRank ticket, returns an extractive source response, ranked resources, and decision trace.
- **Session History**: keeps only new web submissions in local browser storage.

## Pipeline

```text
ticket subject + issue
  -> request-type rules
  -> product-area classifier trained from HackerRank corpus labels
  -> lexical TF-IDF retrieval
  -> MiniLM cosine similarity retrieval
  -> fused score: alpha * lexical_norm + (1 - alpha) * semantic
  -> cross-encoder rerank over top fused candidates
  -> escalation rules: low score, ambiguity, risk terms, privileged/manual actions
  -> top-3 resource recommendations + extractive source response
```

No fine-tuning is used. The persisted `models/area_clf.joblib` is a lightweight scikit-learn product-area classifier built from local corpus labels for the lab demo.

## Evaluation Artifacts

Evaluation data and reports live under `eval/`.

- `eval/datasets/retrieval.jsonl`: pseudo-query retrieval dataset.
- `eval/datasets/classification.csv`: product-area classification dataset.
- `eval/results/retrieval.csv`: retrieval smoke benchmark. In the current 20-query smoke run, `hybrid_best_rerank` reached recall@1 `0.55`, recall@3 `0.65`, and nDCG@10 `0.6447`.
- `eval/results/classification.csv`: 5-fold classifier report. Current best model is TF-IDF logistic regression with weighted F1 about `0.86`.
- `eval/results/*.png`: alpha sweep and confusion matrix plots.

Run the evals:

```bash
python eval/build_datasets.py
python eval/eval_classifier.py
python eval/eval_retrieval.py --limit 20
python eval/compare_retrieval.py --limit 10
```

For a full retrieval sweep, omit `--limit`; it is slower because each query may run cross-encoder reranking on CPU.

## Important Files

- `app.py`: FastAPI server and API endpoints.
- `web/`: static frontend.
- `code/agent.py`: triage orchestration.
- `code/corpus.py`: hybrid retrieval and cached embeddings.
- `code/router.py`: escalation rules.
- `code/explain.py`: extractive response and decision trace helpers.
- `code/area_model.py`: runtime product-area classifier loader.
- `models/area_clf.joblib`: persisted product-area classifier.
- `data/hackerrank/`: active support corpus.
- `data_archive/`: archived corpora excluded from inference.

## CLI Compatibility

The original batch flow still works:

```bash
python code/main.py --input support_tickets/support_tickets/support_tickets.csv --output support_tickets/support_tickets/output.csv
```
