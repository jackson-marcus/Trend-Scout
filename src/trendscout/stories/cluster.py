"""Dedup + online story clustering on embedding similarity.

Near-duplicates (cosine >= dedup threshold) are folded into the earliest copy.
Stories form by greedy online clustering: an article joins the story whose
centroid it is closest to (above the cluster threshold), else starts a new
story. Order-dependent but incremental — the same algorithm serves batch and
streaming ingestion.
"""

from __future__ import annotations

import functools
from dataclasses import dataclass, field

import numpy as np
import pandas as pd

from trendscout.settings import get_config


@functools.lru_cache(maxsize=1)
def _embedder():
    from fastembed import TextEmbedding

    return TextEmbedding("sentence-transformers/all-MiniLM-L6-v2")


def embed(texts: list[str]) -> np.ndarray:
    vectors = np.array([np.asarray(v, dtype=np.float32) for v in _embedder().embed(texts)])
    return vectors / (np.linalg.norm(vectors, axis=1, keepdims=True) + 1e-12)


@dataclass
class Story:
    story_id: int
    centroid: np.ndarray
    article_ids: list[int] = field(default_factory=list)
    titles: list[str] = field(default_factory=list)
    sources: set = field(default_factory=set)
    first_seen: pd.Timestamp | None = None
    last_seen: pd.Timestamp | None = None

    def add(self, article_id: int, title: str, source: str, ts, vector: np.ndarray) -> None:
        n = len(self.article_ids)
        self.centroid = (self.centroid * n + vector) / (n + 1)
        self.centroid /= np.linalg.norm(self.centroid) + 1e-12
        self.article_ids.append(article_id)
        self.titles.append(title)
        self.sources.add(source)
        self.first_seen = ts if self.first_seen is None else min(self.first_seen, ts)
        self.last_seen = ts if self.last_seen is None else max(self.last_seen, ts)

    def as_dict(self) -> dict:
        hours = max((self.last_seen - self.first_seen).total_seconds() / 3600, 0.5)
        return {
            "story_id": self.story_id,
            "headline": self.titles[0],
            "n_articles": len(self.article_ids),
            "n_sources": len(self.sources),
            "velocity_per_hour": round(len(self.article_ids) / hours, 3),
            "first_seen": str(self.first_seen),
            "last_seen": str(self.last_seen),
            "titles": self.titles[:6],
        }


def process(articles: pd.DataFrame) -> tuple[list[Story], pd.DataFrame]:
    """Returns (stories, articles with story_id + duplicate_of columns)."""
    cfg = get_config()
    dedup_t = cfg["dedup"]["similarity_threshold"]
    cluster_t = cfg["stories"]["cluster_threshold"]

    df = articles.sort_values("published").reset_index(drop=True).copy()
    vectors = embed(df["title"].tolist())

    seen_vectors: list[np.ndarray] = []
    seen_ids: list[int] = []
    duplicate_of = []
    stories: list[Story] = []
    story_ids = []

    for i, row in df.iterrows():
        v = vectors[i]
        dup = None
        if seen_vectors:
            sims = np.array(seen_vectors) @ v
            best = int(np.argmax(sims))
            if sims[best] >= dedup_t:
                dup = seen_ids[best]
        duplicate_of.append(dup)
        if dup is not None:
            story_ids.append(story_ids[seen_ids.index(dup)])
            seen_vectors.append(v)
            seen_ids.append(int(row["article_id"]))
            continue

        assigned = None
        if stories:
            centroids = np.array([s.centroid for s in stories])
            sims = centroids @ v
            best = int(np.argmax(sims))
            if sims[best] >= cluster_t:
                assigned = stories[best]
        if assigned is None:
            assigned = Story(story_id=len(stories), centroid=v.copy())
            stories.append(assigned)
        assigned.add(int(row["article_id"]), row["title"], row["source"], row["published"], v)
        story_ids.append(assigned.story_id)
        seen_vectors.append(v)
        seen_ids.append(int(row["article_id"]))

    df["story_id"] = story_ids
    df["duplicate_of"] = duplicate_of
    return stories, df
