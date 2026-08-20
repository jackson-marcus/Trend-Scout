"""Synthetic news corpus with planted stories, near-duplicates, and a burst.

Ground truth (story ids, duplicate pairs, the burst topic/day) is embedded so
dedup, clustering, and burst detection are all measurable.

Usage:
    uv run python scripts/make_news.py
"""

from __future__ import annotations

import sys
from datetime import datetime, timedelta
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from trendscout.settings import get_config, resolve_path

SOURCES = ["WireOne", "GlobalPress", "TechDaily", "MarketWatchr", "CityHerald"]

STORIES = [
    (
        "chipmaker announces breakthrough in low power processors",
        "technology",
        [
            "chipmaker unveils processor breakthrough cutting power use",
            "new low power chip design announced by major manufacturer",
            "processor breakthrough promises longer battery life",
        ],
    ),
    (
        "central bank holds interest rates steady amid inflation fears",
        "economy",
        [
            "interest rates left unchanged as inflation concerns persist",
            "central bank keeps rates on hold citing price pressures",
            "rates held steady while inflation outlook stays uncertain",
        ],
    ),
    (
        "port workers strike disrupts container shipping schedules",
        "logistics",
        [
            "dock strike delays container ships at major port",
            "shipping schedules slip as port labor action continues",
            "container backlog grows during port workers walkout",
        ],
    ),
    (
        "new study links sleep quality to workplace productivity",
        "health",
        [
            "research finds better sleep improves work performance",
            "sleep study shows productivity gains from rest",
            "workplace output tied to sleep quality in new research",
        ],
    ),
    (
        "city approves large scale solar farm on former airfield",
        "energy",
        [
            "solar farm project greenlit at disused airfield",
            "council approves major solar installation",
            "former airfield to host large solar array",
        ],
    ),
    (
        "retailer expands same day delivery to more regions",
        "retail",
        [
            "same day delivery rollout reaches new cities",
            "retail giant widens rapid delivery coverage",
            "delivery expansion brings same day service to more customers",
        ],
    ),
]

BURST_TOPIC = (
    "data breach exposes millions of customer records",
    "security",
    [
        "massive data breach hits customer database",
        "millions of records exposed in security incident",
        "company confirms breach affecting customer data",
        "regulators probe major customer data leak",
        "breach fallout widens as more records surface",
        "security incident exposes customer information at scale",
    ],
)


def generate(seed: int = 42) -> pd.DataFrame:
    rng = np.random.default_rng(seed)
    start = datetime(2026, 8, 1, 6, 0)
    rows = []
    article_id = 1

    for story_id, (headline, topic, variants) in enumerate(STORIES):
        day = int(rng.integers(0, 6))
        base_time = start + timedelta(days=day, hours=int(rng.integers(0, 12)))
        texts = [headline, *variants]
        for i, text in enumerate(texts):
            # The original headline breaks the story at base_time; coverage follows.
            offset = 0 if i == 0 else int(rng.integers(2, 20))
            rows.append(
                {
                    "article_id": article_id,
                    "title": text,
                    "source": SOURCES[i % len(SOURCES)],
                    "published": base_time + timedelta(hours=offset),
                    "topic": topic,
                    "true_story": story_id,
                    "is_near_dup": 0,
                }
            )
            article_id += 1
        # One near-duplicate (syndicated copy, tiny edit) of the headline.
        rows.append(
            {
                "article_id": article_id,
                "title": headline + " today",
                "source": "SyndiCopy",
                "published": base_time + timedelta(hours=1),
                "topic": topic,
                "true_story": story_id,
                "is_near_dup": 1,
            }
        )
        article_id += 1

    # The burst: day 6 explodes with breach coverage.
    headline, topic, variants = BURST_TOPIC
    burst_day = start + timedelta(days=6)
    for i, text in enumerate([headline, *variants]):
        rows.append(
            {
                "article_id": article_id,
                "title": text,
                "source": SOURCES[i % len(SOURCES)],
                "published": burst_day + timedelta(hours=i * 2),
                "topic": topic,
                "true_story": len(STORIES),
                "is_near_dup": 0,
            }
        )
        article_id += 1

    df = pd.DataFrame(rows).sort_values("published").reset_index(drop=True)
    return df


def main() -> None:
    df = generate(get_config()["data"]["seed"])
    out = resolve_path(get_config()["data"]["articles_path"])
    out.parent.mkdir(parents=True, exist_ok=True)
    df.to_parquet(out, index=False)
    print(
        f"Wrote {len(df)} articles ({df['true_story'].nunique()} true stories, 1 planted burst) -> {out}"
    )


if __name__ == "__main__":
    main()
