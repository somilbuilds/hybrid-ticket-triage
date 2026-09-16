from __future__ import annotations

"""Hybrid retrieval for the single-domain HackerRank support corpus.

The corpus is small enough that a transparent in-memory implementation is more
useful than a vector database. The index combines lexical TF-IDF, MiniLM cosine
similarity, and optional cross-encoder reranking. Evaluation can pass
`heldout_text_by_path` so pseudo-query text is removed from its source document
before indexing; otherwise title-query evaluation would collapse into exact
string lookup.
"""

import hashlib
import json
import math
import re
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

from models import EvidenceChunk

TOKEN_RE = re.compile(r"[a-zA-Z0-9_']+")
EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"
RERANK_MODEL = "cross-encoder/ms-marco-MiniLM-L-6-v2"
CACHE_VERSION = 2
MINOR_AREAS = {"engage", "chakra", "uncategorized"}

STOPWORDS = {
    "a",
    "an",
    "and",
    "are",
    "as",
    "at",
    "be",
    "by",
    "for",
    "from",
    "has",
    "have",
    "i",
    "in",
    "is",
    "it",
    "me",
    "my",
    "of",
    "on",
    "or",
    "please",
    "that",
    "the",
    "this",
    "to",
    "was",
    "we",
    "with",
    "you",
    "your",
}


def normalize_product_area(area: str) -> str:
    clean = area.strip().lower()
    return "other" if clean in MINOR_AREAS else clean


def tokenize(text: str) -> list[str]:
    return [
        token.lower()
        for token in TOKEN_RE.findall(text)
        if token.lower() not in STOPWORDS
    ]


def first_tokens(text: str, limit: int) -> str:
    return " ".join(TOKEN_RE.findall(text)[:limit])


class CorpusIndex:
    def __init__(
        self,
        data_dir: Path,
        alpha: float = 0.4,
        cache_dir: Path | None = None,
        use_embeddings: bool = True,
        use_reranker: bool = True,
        heldout_text_by_path: dict[str, list[str]] | None = None,
    ) -> None:
        self._alpha = min(max(alpha, 0.0), 1.0)
        self._cache_dir = cache_dir or data_dir / ".cache"
        self._use_embeddings = use_embeddings
        self._use_reranker = use_reranker
        self._heldout_text_by_path = heldout_text_by_path or {}
        self._docs: list[dict[str, Any]] = []
        self._idf: dict[str, float] = {}
        self._embeddings = None
        self._embedder = None
        self._reranker = None
        self._build(data_dir)

    @property
    def document_count(self) -> int:
        return len(self._docs)

    @property
    def documents(self) -> list[dict[str, Any]]:
        return self._docs

    def set_alpha(self, alpha: float) -> None:
        self._alpha = min(max(alpha, 0.0), 1.0)

    def _build(self, data_dir: Path) -> None:
        doc_freq: defaultdict[str, int] = defaultdict(int)

        for md_path in sorted(data_dir.rglob("*.md")):
            rel = md_path.relative_to(data_dir)
            if rel.parts and rel.parts[0] == ".cache":
                continue
            if rel.parts and rel.parts[0].lower() != "hackerrank":
                continue
            if len(rel.parts) < 3:
                continue
            product_area = normalize_product_area(rel.parts[1]) if len(rel.parts) > 1 else "other"
            try:
                raw_text = md_path.read_text(encoding="utf-8", errors="ignore")
            except OSError:
                continue

            title = self._extract_title(md_path.stem, raw_text)
            content = self._squash_whitespace(raw_text)
            source_path = str(rel).replace("\\", "/")
            index_title, index_content = self._apply_heldout_text(source_path, title, content)
            tokens = tokenize(f"{index_title}\n{index_content}")
            if not tokens:
                continue

            tf = Counter(tokens)
            for token in tf:
                doc_freq[token] += 1

            self._docs.append(
                {
                    "company": "hackerrank",
                    "product_area": product_area,
                    "source_path": source_path,
                    "title": title,
                    "content": content,
                    "index_title": index_title,
                    "index_content": index_content,
                    "tf": tf,
                    "norm": 0.0,
                    "mtime_ns": md_path.stat().st_mtime_ns,
                    "size": md_path.stat().st_size,
                }
            )

        doc_count = max(len(self._docs), 1)
        self._idf = {
            token: math.log((doc_count + 1) / (freq + 1)) + 1.0
            for token, freq in doc_freq.items()
        }

        for doc in self._docs:
            norm_sq = 0.0
            for token, count in doc["tf"].items():
                weight = count * self._idf.get(token, 1.0)
                norm_sq += weight * weight
            doc["norm"] = math.sqrt(norm_sq) if norm_sq > 0 else 1.0

        if self._use_embeddings:
            self._embeddings = self._load_or_build_embeddings()

    @staticmethod
    def _extract_title(stem: str, text: str) -> str:
        for line in text.splitlines():
            line = line.strip()
            if line.startswith("#"):
                return line.lstrip("#").strip() or stem
        return stem.replace("-", " ")

    @staticmethod
    def _squash_whitespace(text: str) -> str:
        if text.startswith("---"):
            parts = text.split("---", 2)
            if len(parts) == 3:
                text = parts[2]
        return "\n".join(line.rstrip() for line in text.splitlines())

    def _apply_heldout_text(self, source_path: str, title: str, content: str) -> tuple[str, str]:
        index_title = title
        index_content = content
        for heldout in self._heldout_text_by_path.get(source_path, []):
            clean = heldout.strip()
            if clean:
                index_title = index_title.replace(clean, " ")
                index_content = index_content.replace(clean, " ")
        return index_title, index_content

    def _corpus_signature(self) -> str:
        payload = {
            "version": CACHE_VERSION,
            "model": EMBEDDING_MODEL,
            "heldout": self._heldout_text_by_path,
            "docs": [
                [doc["source_path"], doc["mtime_ns"], doc["size"]]
                for doc in self._docs
            ],
        }
        raw = json.dumps(payload, sort_keys=True).encode("utf-8")
        return hashlib.sha256(raw).hexdigest()[:16]

    def _load_or_build_embeddings(self):
        import numpy as np
        from sentence_transformers import SentenceTransformer

        self._cache_dir.mkdir(parents=True, exist_ok=True)
        signature = self._corpus_signature()
        cache_path = self._cache_dir / f"embeddings-{signature}.npz"
        if cache_path.exists():
            return np.load(cache_path)["embeddings"]

        self._embedder = SentenceTransformer(EMBEDDING_MODEL, device="cpu")
        texts = [
            f"{doc['index_title']}\n{doc['index_content'][:1800]}"
            for doc in self._docs
        ]
        embeddings = self._embedder.encode(
            texts,
            batch_size=32,
            convert_to_numpy=True,
            normalize_embeddings=True,
            show_progress_bar=False,
        )
        np.savez_compressed(cache_path, embeddings=embeddings)
        return embeddings

    def _embedding_model(self):
        if self._embedder is None:
            from sentence_transformers import SentenceTransformer

            self._embedder = SentenceTransformer(EMBEDDING_MODEL, device="cpu")
        return self._embedder

    def _rerank_model(self):
        if self._reranker is None:
            from sentence_transformers import CrossEncoder

            self._reranker = CrossEncoder(RERANK_MODEL, device="cpu")
        return self._reranker

    def lexical_search(self, query: str, top_k: int) -> list[EvidenceChunk]:
        candidates = self._lexical_candidates(query)
        candidates.sort(key=lambda item: item["lexical_score"], reverse=True)
        return [
            self._to_chunk(item, query_tokens=tokenize(query), score_key="lexical_score")
            for item in candidates[:top_k]
        ]

    def semantic_search(self, query: str, top_k: int) -> list[EvidenceChunk]:
        semantic_scores = self._semantic_scores(query)
        if semantic_scores is None:
            return []
        candidates = []
        for doc_index, doc in enumerate(self._docs):
            score = max(0.0, float(semantic_scores[doc_index]))
            if score <= 0:
                continue
            candidates.append(
                {
                    "doc_index": doc_index,
                    "doc": doc,
                    "lexical_score": 0.0,
                    "lexical_norm": 0.0,
                    "semantic_score": score,
                    "final_score": score,
                    "rerank_score": 0.0,
                }
            )
        candidates.sort(key=lambda item: item["semantic_score"], reverse=True)
        return [self._to_chunk(item, tokenize(query)) for item in candidates[:top_k]]

    def search(self, query: str, top_k: int, rerank_pool: int = 10) -> list[EvidenceChunk]:
        q_tokens = tokenize(query)
        if not q_tokens:
            return []

        lexical_by_index = {
            item["doc_index"]: item["lexical_score"]
            for item in self._lexical_candidates(query)
        }
        semantic_scores = self._semantic_scores(query)
        if semantic_scores is None and not lexical_by_index:
            return []

        max_lexical = max(lexical_by_index.values(), default=1.0) or 1.0
        fused = []
        for doc_index, doc in enumerate(self._docs):
            lexical_score = lexical_by_index.get(doc_index, 0.0)
            semantic = float(semantic_scores[doc_index]) if semantic_scores is not None else 0.0
            semantic = max(0.0, semantic)
            lexical_norm = lexical_score / max_lexical
            final_score = (self._alpha * lexical_norm) + ((1.0 - self._alpha) * semantic)
            if final_score <= 0:
                continue
            fused.append(
                {
                    "doc_index": doc_index,
                    "doc": doc,
                    "lexical_score": lexical_score,
                    "lexical_norm": lexical_norm,
                    "semantic_score": semantic,
                    "final_score": final_score,
                    "rerank_score": 0.0,
                }
            )

        fused.sort(key=lambda item: item["final_score"], reverse=True)
        pool = fused[: max(top_k, rerank_pool)]

        if self._use_reranker and pool:
            reranker = self._rerank_model()
            pairs = [
                [query, f"{item['doc']['title']}\n{item['doc']['content'][:900]}"]
                for item in pool
            ]
            rerank_scores = reranker.predict(pairs)
            for item, rerank_score in zip(pool, rerank_scores):
                item["rerank_score"] = float(rerank_score)
            pool.sort(key=lambda item: item["rerank_score"], reverse=True)

        return [self._to_chunk(item, q_tokens) for item in pool[:top_k]]

    def _lexical_candidates(self, query: str) -> list[dict[str, Any]]:
        q_tokens = tokenize(query)
        if not q_tokens:
            return []

        q_tf = Counter(q_tokens)
        q_norm_sq = 0.0
        for token, count in q_tf.items():
            weight = count * self._idf.get(token, 1.0)
            q_norm_sq += weight * weight
        q_norm = math.sqrt(q_norm_sq) if q_norm_sq > 0 else 1.0

        candidates = []
        for index, doc in enumerate(self._docs):
            dot = 0.0
            token_contrib: dict[str, float] = {}
            for token, q_count in q_tf.items():
                d_count = doc["tf"].get(token, 0)
                if d_count == 0:
                    continue
                idf = self._idf.get(token, 1.0)
                contrib = (q_count * idf) * (d_count * idf)
                dot += contrib
                token_contrib[token] = contrib
            if dot <= 0:
                continue

            lexical_score = dot / (q_norm * doc["norm"])
            total = sum(token_contrib.values()) or 1.0
            candidates.append(
                {
                    "doc_index": index,
                    "doc": doc,
                    "lexical_score": lexical_score,
                    "token_contrib": {
                        token: value / total
                        for token, value in sorted(
                            token_contrib.items(), key=lambda item: item[1], reverse=True
                        )
                    },
                }
            )
        return candidates

    def _semantic_scores(self, query: str):
        if self._embeddings is None:
            return None
        embedder = self._embedding_model()
        query_embedding = embedder.encode(
            [query],
            convert_to_numpy=True,
            normalize_embeddings=True,
            show_progress_bar=False,
        )[0]
        return self._embeddings @ query_embedding

    def _to_chunk(
        self,
        item: dict[str, Any],
        query_tokens: list[str],
        score_key: str = "final_score",
    ) -> EvidenceChunk:
        doc = item["doc"]
        matched = [
            token
            for token, _ in Counter(query_tokens).most_common()
            if token in doc["tf"]
        ][:8]
        score = float(item.get(score_key, item.get("final_score", 0.0)))
        lexical = float(item.get("lexical_norm", item.get("lexical_score", 0.0)))
        semantic = float(item.get("semantic_score", 0.0))
        rerank = float(item.get("rerank_score", 0.0))
        explanation = self._explain_match(matched, lexical, semantic, rerank)
        return EvidenceChunk(
            company=doc["company"],
            product_area=doc["product_area"],
            source_path=doc["source_path"],
            title=doc["title"],
            content=doc["content"][:900],
            score=score,
            lexical_score=lexical,
            semantic_score=semantic,
            rerank_score=rerank,
            matched_keywords=matched,
            match_explanation=explanation,
            lexical_attribution=item.get("token_contrib", {}),
        )

    @staticmethod
    def _explain_match(
        matched_keywords: list[str],
        lexical_score: float,
        semantic_score: float,
        rerank_score: float,
    ) -> str:
        keyword_text = ", ".join(matched_keywords[:4]) if matched_keywords else "semantic similarity"
        if rerank_score:
            return (
                f"Ranked after cross-encoder reranking; matched {keyword_text} "
                f"with lexical={lexical_score:.2f} and semantic={semantic_score:.2f}."
            )
        return (
            f"Ranked by hybrid retrieval; matched {keyword_text} "
            f"with lexical={lexical_score:.2f} and semantic={semantic_score:.2f}."
        )
