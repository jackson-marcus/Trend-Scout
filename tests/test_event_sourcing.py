"""Unit tests for the Event Sourcing Architecture in TrendScout."""

from trendscout.events.contracts import (
    ArticleIngestedEvent,
    BurstDetectedEvent,
)
from trendscout.events.store import EventStore
from trendscout.projections.projections import (
    BurstLeaderboardProjection,
    TopicVolumeProjection,
)


def test_event_store_append_and_read():
    store = EventStore()
    evt1 = ArticleIngestedEvent(event_id="E-1", article_id="A-1", topic="ai_safety")
    evt2 = ArticleIngestedEvent(event_id="E-2", article_id="A-2", topic="quantum")

    store.append(evt1)
    store.append(evt2)

    assert store.count() == 2
    events = list(store.read_stream())
    assert events[0].event_id == "E-1"
    assert events[1].event_id == "E-2"


def test_topic_volume_projection_and_rebuild():
    store = EventStore()
    store.append(
        ArticleIngestedEvent(
            event_id="E-1", article_id="A-1", topic="ai_safety", published_date="2026-08-20"
        )
    )
    store.append(
        ArticleIngestedEvent(
            event_id="E-2", article_id="A-2", topic="ai_safety", published_date="2026-08-20"
        )
    )
    store.append(
        ArticleIngestedEvent(
            event_id="E-3", article_id="A-3", topic="biotech", published_date="2026-08-20"
        )
    )

    # Hydrate projection by replaying store
    proj = TopicVolumeProjection()
    proj.rebuild_from_store(store)

    assert proj.get_topic_count("ai_safety") == 2
    assert proj.get_topic_count("biotech") == 1
    assert proj.get_topic_count("quantum") == 0


def test_burst_leaderboard_projection():
    store = EventStore()
    store.append(
        BurstDetectedEvent(
            event_id="B-1",
            topic="superconductors",
            day="2026-08-20",
            today_count=50,
            trailing_mean=5.0,
            velocity_ratio=10.0,
        )
    )
    store.append(
        BurstDetectedEvent(
            event_id="B-2",
            topic="battery_tech",
            day="2026-08-20",
            today_count=15,
            trailing_mean=5.0,
            velocity_ratio=3.0,
        )
    )

    proj = BurstLeaderboardProjection()
    proj.rebuild_from_store(store)

    bursts = proj.get_recent_bursts(limit=5)
    assert len(bursts) == 2
    assert bursts[0]["topic"] == "superconductors"
    assert bursts[0]["velocity_ratio"] == 10.0
