"""burst_detector — feature processing sink for SocialSignal events."""

from __future__ import annotations

from trendscout.streams.schemas import REQUIRED_FIELDS, StreamEvent


class FeatureProcessor:
    """Turn stream payloads into a running feature snapshot."""

    name = "burst_detector"

    def __init__(self) -> None:
        self.seen = 0
        self.snapshot: dict[str, float] = dict.fromkeys(REQUIRED_FIELDS, 0.0)

    def handle(self, event: StreamEvent) -> dict[str, float]:
        self.seen += 1
        for key, value in event.payload.items():
            if isinstance(value, int | float):
                self.snapshot[key] = self.snapshot.get(key, 0.0) + float(value)
            else:
                self.snapshot[key] = self.snapshot.get(key, 0.0) + 1.0
        return dict(self.snapshot)


class EnrichmentWorker(FeatureProcessor):
    """Flagship extra: tag bursts after a volume threshold."""

    def handle(self, event: StreamEvent) -> dict[str, float]:
        snapshot = super().handle(event)
        snapshot["burst"] = float(self.seen >= 3)
        return snapshot


class SinkWorker:
    """Flagship extra: append processed snapshots to an audit sink."""

    def __init__(self) -> None:
        self.rows: list[dict[str, float]] = []

    def write(self, snapshot: dict[str, float]) -> None:
        self.rows.append(dict(snapshot))
