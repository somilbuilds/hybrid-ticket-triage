from __future__ import annotations

"""Evaluate product-area classifiers and persist the best final model."""

import argparse
import csv
import random
import re
import sys
from pathlib import Path

import joblib
import matplotlib.pyplot as plt
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    ConfusionMatrixDisplay,
    accuracy_score,
    classification_report,
    confusion_matrix,
    f1_score,
    precision_recall_fscore_support,
)
from sklearn.model_selection import StratifiedKFold, cross_val_predict
from sklearn.pipeline import Pipeline

ROOT = Path(__file__).resolve().parents[1]
CODE_DIR = ROOT / "code"
if str(CODE_DIR) not in sys.path:
    sys.path.insert(0, str(CODE_DIR))

from corpus import EMBEDDING_MODEL  # noqa: E402

SEED = 42

KEYWORD_RULES = [
    ("screen", re.compile(r"\b(test|assessment|candidate|proctor|score|invite)\b", re.I)),
    ("integrations", re.compile(r"\b(integration|greenhouse|workday|lever|ashby|sso|saml|scim)\b", re.I)),
    ("settings", re.compile(r"\b(setting|account|team|role|permission|password|email)\b", re.I)),
    ("library", re.compile(r"\b(question|library|coding|test case|checker|template)\b", re.I)),
    ("interviews", re.compile(r"\b(interview|scorecard|whiteboard|audio|video|zoom)\b", re.I)),
    ("hackerrank_community", re.compile(r"\b(community|practice|challenge|contest|certificate)\b", re.I)),
    ("skillup", re.compile(r"\b(skillup|certification|learn|license|employee)\b", re.I)),
    ("general-help", re.compile(r"\b(contact|release|academy|support|maintenance)\b", re.I)),
]


def load_rows(path: Path) -> tuple[list[str], list[str]]:
    texts: list[str] = []
    labels: list[str] = []
    with path.open("r", encoding="utf-8", newline="") as handle:
        for row in csv.DictReader(handle):
            texts.append(row["text"])
            labels.append(row["label"])
    return texts, labels


def keyword_predict(text: str) -> str:
    for label, pattern in KEYWORD_RULES:
        if pattern.search(text):
            return label
    return "other"


def rows_for_report(name: str, y_true: list[str], y_pred: list[str]) -> list[dict[str, str]]:
    labels = sorted(set(y_true) | set(y_pred))
    precision, recall, f1, support = precision_recall_fscore_support(
        y_true,
        y_pred,
        labels=labels,
        zero_division=0,
    )
    rows = []
    for label, p, r, f, s in zip(labels, precision, recall, f1, support):
        rows.append(
            {
                "model": name,
                "class": label,
                "precision": f"{p:.4f}",
                "recall": f"{r:.4f}",
                "f1": f"{f:.4f}",
                "support": str(int(s)),
                "accuracy": "",
                "macro_f1": "",
            }
        )
    rows.append(
        {
            "model": name,
            "class": "__overall__",
            "precision": "",
            "recall": "",
            "f1": "",
            "support": str(len(y_true)),
            "accuracy": f"{accuracy_score(y_true, y_pred):.4f}",
            "macro_f1": f"{f1_score(y_true, y_pred, average='macro'):.4f}",
        }
    )
    return rows


def plot_confusion(y_true: list[str], y_pred: list[str], labels: list[str], out_path: Path) -> None:
    matrix = confusion_matrix(y_true, y_pred, labels=labels)
    fig, ax = plt.subplots(figsize=(9, 8))
    ConfusionMatrixDisplay(matrix, display_labels=labels).plot(
        ax=ax,
        xticks_rotation=45,
        colorbar=False,
        values_format="d",
    )
    ax.set_title("Best product-area classifier confusion matrix")
    plt.tight_layout()
    plt.savefig(out_path, dpi=150)
    plt.close(fig)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--dataset", default=str(ROOT / "eval" / "datasets" / "classification.csv"))
    args = parser.parse_args()

    random.seed(SEED)
    np.random.seed(SEED)
    texts, labels = load_rows(Path(args.dataset))
    unique_labels = sorted(set(labels))
    cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=SEED)

    result_dir = ROOT / "eval" / "results"
    result_dir.mkdir(parents=True, exist_ok=True)
    model_dir = ROOT / "models"
    model_dir.mkdir(parents=True, exist_ok=True)

    reports: list[dict[str, str]] = []
    predictions: dict[str, list[str]] = {}

    keyword_pred = [keyword_predict(text) for text in texts]
    predictions["keyword_rules"] = keyword_pred
    reports.extend(rows_for_report("keyword_rules", labels, keyword_pred))

    tfidf_pipeline = Pipeline(
        [
            ("tfidf", TfidfVectorizer(max_features=12000, ngram_range=(1, 2), min_df=2)),
            ("clf", LogisticRegression(max_iter=1500, class_weight="balanced", random_state=SEED)),
        ]
    )
    tfidf_pred = cross_val_predict(tfidf_pipeline, texts, labels, cv=cv)
    predictions["tfidf_logreg"] = list(tfidf_pred)
    reports.extend(rows_for_report("tfidf_logreg", labels, list(tfidf_pred)))

    from sentence_transformers import SentenceTransformer

    embedder = SentenceTransformer(EMBEDDING_MODEL, device="cpu")
    embeddings = embedder.encode(
        texts,
        batch_size=32,
        convert_to_numpy=True,
        normalize_embeddings=True,
        show_progress_bar=False,
    )
    mini_clf = LogisticRegression(max_iter=1500, class_weight="balanced", random_state=SEED)
    mini_pred = cross_val_predict(mini_clf, embeddings, labels, cv=cv)
    predictions["minilm_logreg"] = list(mini_pred)
    reports.extend(rows_for_report("minilm_logreg", labels, list(mini_pred)))

    out_csv = result_dir / "classification.csv"
    fieldnames = ["model", "class", "precision", "recall", "f1", "support", "accuracy", "macro_f1"]
    with out_csv.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(reports)

    overall = [row for row in reports if row["class"] == "__overall__"]
    best = max(overall, key=lambda row: float(row["macro_f1"]))
    best_name = best["model"]

    if best_name == "minilm_logreg":
        final_clf = LogisticRegression(max_iter=1500, class_weight="balanced", random_state=SEED)
        final_clf.fit(embeddings, labels)
        bundle = {
            "kind": "minilm",
            "embedding_model": EMBEDDING_MODEL,
            "classifier": final_clf,
            "labels": list(final_clf.classes_),
        }
    else:
        if best_name == "keyword_rules":
            best_name = "tfidf_logreg"
        final_pipeline = tfidf_pipeline.fit(texts, labels)
        bundle = {
            "kind": "tfidf",
            "vectorizer": final_pipeline.named_steps["tfidf"],
            "classifier": final_pipeline.named_steps["clf"],
            "labels": list(final_pipeline.named_steps["clf"].classes_),
        }

    joblib.dump(bundle, model_dir / "area_clf.joblib")
    plot_confusion(labels, predictions[best_name], unique_labels, result_dir / "classification_confusion.png")
    print(classification_report(labels, predictions[best_name], zero_division=0))
    print(f"Best model: {best_name} macro_f1={best['macro_f1']}")
    print(f"Wrote classification metrics to {out_csv}")
    print(f"Wrote classifier to {model_dir / 'area_clf.joblib'}")


if __name__ == "__main__":
    main()
