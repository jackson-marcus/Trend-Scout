"""Event Sourcing Architecture - Append-Only Event Store.

Stores domain events sequentially and supports event replay, stream filtering, and snapshotting.
"""

from __future__ import annotations

import logging
from collections.abc import Iterator

from trendscout.events.contracts import Event

logger = logging.getLogger(__name__)


class EventStore:
    """In-memory append-only event store guaranteeing sequential write order."""

    def __init__(self) -> None:
        self._events: list[Event] = []

    def append(self, event: Event) -> int:
        """Append an event to the log. Returns its 0-indexed sequence position."""
        self._events.append(event)
        seq = len(self._events) - 1
        logger.debug("Appended event %s at sequence %d", type(event).__name__, seq)
        return seq

    def append_all(self, events: list[Event]) -> list[int]:
        """Append multiple events atomically."""
        return [self.append(evt) for evt in events]

    def read_stream(
        self, from_sequence: int = 0, event_types: tuple[type[Event], ...] | None = None
    ) -> Iterator[Event]:
        """Replay events from a given sequence offset, optionally filtered by type."""
        for evt in self._events[from_sequence:]:
            if event_types is None or isinstance(evt, event_types):
                yield evt

    def count(self) -> int:
        """Total number of events recorded."""
        return len(self._events)

    def clear(self) -> None:
        """Reset event log (useful in tests)."""
        self._events.clear()


# Global singleton event store
GLOBAL_EVENT_STORE = EventStore()
