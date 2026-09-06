# NLP Support Triage Web App - Project Plan

## Goal

Turn the old HackerRank Orchestrate CLI triage agent into a local UI-based NLP lab application. The app should demonstrate support-ticket triage with an explainable ML/NLP pipeline, not just produce a CSV.

## Current Useful Core

Keep the Python triage engine in `code/`:

- `agent.py`: orchestrates ticket triage.
- `corpus.py`: builds hybrid lexical + semantic retrieval over markdown support docs.
- `classifier.py`: infers company, request type, and product area.
- `router.py`: decides reply vs escalation.
- ranked recommendations replace generated support responses.

The current logic is lightweight enough for a laptop. It does not do training or fine-tuning. It uses deterministic lexical scoring, pretrained sentence embeddings, pretrained reranking, and rules, which is appropriate for a lab demo because students can inspect the full decision path.

## Desired Product

Build a website with:

1. Home page
   - App name.
   - Short guidelines.
   - Light/dark mode.
   - Two main actions:
     - Check existing dataset and status.
     - Enter your query/ticket.

2. Existing dataset view
   - Show tickets in a clean table/card layout.
   - Include company, subject, issue preview, status, product area, and request type.
   - Show summary stats: total tickets, replied vs escalated, company distribution, request-type distribution.

3. New ticket triage view
   - Let user choose HackerRank, Claude, or Visa.
   - Each company should have its own accent color and visual treatment.
   - User enters subject and issue.
   - Backend runs the existing triage engine.
   - UI shows prediction, recommended resources, confidence, retrieval scores, and routing details.
   - Add the result to local session history, not to the original dataset.

4. History view
   - Show only user-entered tickets from the web app session/storage.
   - Do not mutate the original hackathon CSV files.

## Implementation Plan

- Use FastAPI for the backend.
- Serve a static frontend from `web/`.
- Add API endpoints:
  - `GET /api/health`
  - `GET /api/dataset`
  - `POST /api/triage`
  - `GET /api/corpus-stats`
- Keep the CLI runnable for compatibility, but the web app becomes the main interface.
- Improve `SupportTriageAgent` with a detailed prediction method so the frontend can display evidence and scores.

## Cleanup Plan

Remove hackathon-only files from the active project root:

- `AGENTS.md`
- `CLAUDE.md`
- `problem_statement.md`
- `evalutation_criteria.md`
- `code-zip.zip`
- root `log.txt`
- macOS extraction folder `support_tickets/__MACOSX`
- old ignored `support_tickets_github/` trial outputs

Keep:

- `code/`
- `data/`
- `support_tickets/support_tickets/*.csv`
- `.env` / `.gitignore`
- new web app files and docs

## Notes For Future Work

- If accuracy needs improvement, first tune rules, retrieval thresholds, and reranking blend using the sample tickets. Do not jump to fine-tuning.
- A possible later upgrade is evaluating alternative embedding or reranker models, but keep the system inference-only for the lab.
- Keep secrets in `.env`; never hardcode API keys.
