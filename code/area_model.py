from __future__ import annotations

"""Runtime product-area classifier interface.

The persisted model is trained by `eval/eval_classifier.py` from corpus folder
labels. It intentionally exposes one small function: `predict_area(text)`.
"""

from functools import lru_cache
from pathlib import Path
from typing import Any

import joblib

MODEL_PATH = Path(__file__).resolve().parents[1] / "models" / "area_clf.joblib"


@lru_cache(maxsize=1)
def _load_model() -> dict[str, Any] | None:
    if not MODEL_PATH.exists():
        return None
    return joblib.load(MODEL_PATH)


@lru_cache(maxsize=1)
def _embedder(model_name: str):
    from sentence_transformers import SentenceTransformer

    return SentenceTransformer(model_name, device="cpu")


def predict_area(text: str) -> tuple[str, float]:
    bundle = _load_model()
    if bundle is None:
        return "other", 0.0

    kind = bundle["kind"]
    labels = bundle["labels"]
    clf = bundle["classifier"]
    if kind == "tfidf":
        matrix = bundle["vectorizer"].transform([text])
        probs = clf.predict_proba(matrix)[0]
    elif kind == "minilm":
        embedding = _embedder(bundle["embedding_model"]).encode(
            [text],
            convert_to_numpy=True,
            normalize_embeddings=True,
            show_progress_bar=False,
        )
        probs = clf.predict_proba(embedding)[0]
    else:
        return "other", 0.0

    best_index = int(probs.argmax())
    return labels[best_index], float(probs[best_index])
