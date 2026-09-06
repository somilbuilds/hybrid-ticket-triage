# Agent Handoff

## Current Direction

The user wants this repository converted from an old CLI hackathon submission into a UI-based NLP lab software project.

Do not continue the old hackathon onboarding/logging workflow. The user explicitly asked to remove the unwanted hackathon `AGENTS.md` behavior and said there should be no logging now.

## What To Build

Build a local website for the existing support triage engine:

- Home page with app name, basic guidelines, dark/light mode, and two main buttons.
- Dataset view showing existing tickets and their predicted status/company/product area neatly.
- Query view where the user selects one of three companies:
  - HackerRank
  - Claude
  - Visa
- Each company option should have a distinct accent color and UI treatment.
- User enters a subject and issue.
- Backend runs the existing Python triage pipeline.
- UI displays:
  - replied/escalated status
  - product area
  - request type
  - top-3 recommended resources
  - justification
  - confidence/routing information
  - lexical, semantic, fused, and rerank scores
  - matched keywords and one-line match explanations
  - useful NLP/ML stats
- Add submitted tickets to web-app history only. Do not modify original CSV datasets.

## Recommended Architecture

- Backend: FastAPI in `app.py`.
- Frontend: static HTML/CSS/JS in `web/`.
- Existing engine: reuse `code/SupportTriageAgent`.
- Add a detailed prediction method to `SupportTriageAgent` instead of duplicating pipeline logic in the API.

## Important Files

- `code/agent.py`: main pipeline.
- `code/corpus.py`: TF-IDF retriever.
- `code/classifier.py`: request/company/product rules.
- `code/router.py`: escalation decision logic.
- `code/models.py`: dataclasses.
- `support_tickets/support_tickets/sample_support_tickets.csv`: labeled sample data.
- `support_tickets/support_tickets/support_tickets.csv`: unlabeled/original dataset.

## Cleanup

The active project should not keep old hackathon management files. Remove old root artifacts after the new plan files exist:

- `AGENTS.md`
- `CLAUDE.md`
- `problem_statement.md`
- `evalutation_criteria.md`
- `code-zip.zip`
- `log.txt`
- `support_tickets/__MACOSX`
- `support_tickets_github/`

## Accuracy And Training

Do not train or fine-tune a model unless the user explicitly asks. The current method is hybrid lexical + pretrained MiniLM embeddings + pretrained cross-encoder reranking plus rules, which is laptop-friendly and explainable for an NLP lab.

If improving accuracy:

1. Run sample tickets.
2. Compare predicted columns with expected columns.
3. Adjust retrieval thresholds, product-area rules, and escalation rules.
4. Keep the app explainable.

## Final Expected State

The user should be able to run:

```bash
pip install -r requirements.txt
uvicorn app:app --reload
```

Then open the local URL and use the web dashboard.
