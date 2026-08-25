"""Event Sourcing Architecture - Projections Package."""

from trendscout.projections.projections import (
    BaseProjection,
    BurstLeaderboardProjection,
    TopicVolumeProjection,
)

__all__ = [
    "BaseProjection",
    "BurstLeaderboardProjection",
    "TopicVolumeProjection",
]
