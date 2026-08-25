"""Event Sourcing Architecture - Events Package."""

from trendscout.events.contracts import (
    ArticleIngestedEvent,
    BurstDetectedEvent,
    Event,
    StoryClusterFormedEvent,
    TrendBriefGeneratedEvent,
)
from trendscout.events.store import GLOBAL_EVENT_STORE, EventStore

__all__ = [
    "GLOBAL_EVENT_STORE",
    "ArticleIngestedEvent",
    "BurstDetectedEvent",
    "Event",
    "EventStore",
    "StoryClusterFormedEvent",
    "TrendBriefGeneratedEvent",
]
