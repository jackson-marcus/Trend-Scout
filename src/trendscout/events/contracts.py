"""Event Sourcing Architecture - Domain Events.

Typed, immutable domain events recorded in the append-only event log.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime


def _utc_now() -> str:
    return datetime.now(UTC).isoformat()


@dataclass(frozen=True)
class Event:
    """Base interface for all event-sourced domain events."""

    event_id: str
    timestamp: str = field(default_factory=_utc_now)
    version: int = 1


@dataclass(frozen=True)
class ArticleIngestedEvent(Event):
    """Emitted when a news article or RSS post is ingested."""

    article_id: str = ""
    title: str = ""
    topic: str = ""
    source: str = ""
    published_date: str = ""
    text_snippet: str = ""


@dataclass(frozen=True)
class StoryClusterFormedEvent(Event):
    """Emitted when semantic clustering groups articles into a coalesced story."""

    cluster_id: str = ""
    topic: str = ""
    headline: str = ""
    article_ids: list[str] = field(default_factory=list)
    cohesion_score: float = 0.0


@dataclass(frozen=True)
class BurstDetectedEvent(Event):
    """Emitted when statistical volume of a topic exceeds Poisson baseline."""

    topic: str = ""
    day: str = ""
    today_count: int = 0
    trailing_mean: float = 0.0
    velocity_ratio: float = 1.0


@dataclass(frozen=True)
class TrendBriefGeneratedEvent(Event):
    """Emitted when LLM synthesizes an intelligence digest."""

    brief_id: str = ""
    summary: str = ""
    key_drivers: list[str] = field(default_factory=list)
