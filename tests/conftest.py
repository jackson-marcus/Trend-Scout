"""Fixtures: planted-truth news corpus + stub embedder (no model downloads)."""

from __future__ import annotations

import hashlib
import re
import sys
from pathlib import Path

import numpy as np
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from make_news import generate

import trendscout.stories.cluster as cluster_mod


class StubEmbedder:
    """Bag-of-words hash embedding — near-dup titles stay highly similar."""

    def embed(self, texts):
        for text in texts:
            vec = np.zeros(96, dtype=np.float32)
            for token in re.findall(r"[a-z0-9]+", str(text).lower()):
                vec[int(hashlib.md5(token.encode()).hexdigest(), 16) % 96] += 1.0
            yield vec


@pytest.fixture(scope="session")
def articles():
    return generate(seed=11)


@pytest.fixture(autouse=True)
def stub_embedder(monkeypatch):
    """Stub embeddings are lexical (token overlap), unlike MiniLM's semantic
    space — so tests run with thresholds tuned for the stub space while the
    shipped config stays tuned for MiniLM."""
    import fastembed

    from trendscout.settings import get_config

    monkeypatch.setattr(fastembed, "TextEmbedding", lambda *a, **k: StubEmbedder())
    cfg = get_config()
    original = (cfg["dedup"]["similarity_threshold"], cfg["stories"]["cluster_threshold"])
    cfg["dedup"]["similarity_threshold"] = 0.90
    cfg["stories"]["cluster_threshold"] = 0.25
    cluster_mod._embedder.cache_clear()
    yield
    cfg["dedup"]["similarity_threshold"], cfg["stories"]["cluster_threshold"] = original
    cluster_mod._embedder.cache_clear()
