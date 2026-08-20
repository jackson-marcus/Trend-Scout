"""Burst detection: which topics/stories are exploding today vs their baseline."""

from __future__ import annotations

import pandas as pd

from trendscout.settings import get_config


def daily_counts(articles: pd.DataFrame, by: str = "topic") -> pd.DataFrame:
    df = articles.copy()
    df["day"] = pd.to_datetime(df["published"]).dt.date
    return df.groupby(["day", by]).size().reset_index(name="n")


def detect_bursts(articles: pd.DataFrame, by: str = "topic") -> list[dict]:
    cfg = get_config()["trends"]
    counts = daily_counts(articles, by)
    if counts.empty:
        return []
    days = sorted(counts["day"].unique())
    latest = days[-1]
    trailing = [d for d in days if d < latest][-cfg["burst_trailing_days"] :]

    bursts = []
    for key, group in counts.groupby(by):
        today = int(group.loc[group["day"] == latest, "n"].sum())
        base = group[group["day"].isin(trailing)]["n"]
        baseline = float(base.mean()) if len(base) else 0.0
        if today >= cfg["burst_min_articles"] and (
            baseline == 0.0 or today >= cfg["burst_ratio"] * baseline
        ):
            bursts.append(
                {
                    "key": str(key),
                    "today": today,
                    "trailing_mean": round(baseline, 2),
                    "ratio": round(today / baseline, 2) if baseline else None,
                    "day": str(latest),
                }
            )
    return sorted(bursts, key=lambda b: -b["today"])
