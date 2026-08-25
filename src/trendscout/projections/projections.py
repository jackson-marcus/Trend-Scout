"""Event Sourcing Architecture - Projections Engine.

Rebuildable in-memory read models hydrated purely by replaying event streams.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from collections import defaultdict
from typing import Any

from trendscout.events.contracts import (
    ArticleIngestedEvent,
    BurstDetectedEvent,
    Event,
)
from trendscout.events.store import EventStore


class BaseProjection(ABC):
    """Abstract base class for a rebuildable read model projection."""

    @abstractmethod
    def apply(self, event: Event) -> None:
        """Update internal state in response to a domain event."""
        ...

    @abstractmethod
    def reset(self) -> None:
        """Clear projection state."""
        ...

    def rebuild_from_store(self, store: EventStore) -> None:
        """Replay all historical events to rebuild the projection state from scratch."""
        self.reset()
        for evt in store.read_stream():
            self.apply(evt)


class TopicVolumeProjection(BaseProjection):
    """Projection maintaining total ingested article counts per topic."""

    def __init__(self) -> None:
        self.counts: dict[str, int] = defaultdict(int)
        self.daily_counts: dict[str, dict[str, int]] = defaultdict(lambda: defaultdict(int))

    def reset(self) -> None:
        self.counts.clear()
        self.daily_counts.clear()

    def apply(self, event: Event) -> None:
        if isinstance(event, ArticleIngestedEvent):
            self.counts[event.topic] += 1
            if event.published_date:
                day = event.published_date.split("T")[0]
                self.daily_counts[day][event.topic] += 1

    def get_topic_count(self, topic: str) -> int:
        return self.counts.get(topic, 0)

    def get_leaderboard(self, top_n: int = 10) -> list[tuple[str, int]]:
        return sorted(self.counts.items(), key=lambda x: -x[1])[:top_n]


class BurstLeaderboardProjection(BaseProjection):
    """Projection tracking active statistical burst alerts."""

    def __init__(self) -> None:
        self.bursts: list[dict[str, Any]] = []

    def reset(self) -> None:
        self.bursts.clear()

    def apply(self, event: Event) -> None:
        if isinstance(event, BurstDetectedEvent):
            self.bursts.append(
                {
                    "topic": event.topic,
                    "day": event.day,
                    "today_count": event.today_count,
                    "trailing_mean": event.trailing_mean,
                    "velocity_ratio": event.velocity_ratio,
                    "timestamp": event.timestamp,
                }
            )

    def get_recent_bursts(self, limit: int = 10) -> list[dict[str, Any]]:
        return sorted(self.bursts, key=lambda b: -b.get("velocity_ratio", 0))[:limit]
