"""Structured run traces.

Records one span per agent per phase (round_N / final) with start/end
timestamps and status.  Written to ``output/trace.json`` after a run and
re-loadable for latency analysis.  When the optional OpenTelemetry SDK is
installed, :meth:`RunTrace.export_otel` emits equivalent spans; otherwise it
is a safe no-op.
"""

from __future__ import annotations

import json
import logging
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)

TRACE_FILENAME = "trace.json"


@dataclass
class Span:
    """A single timed unit of work for one agent in one phase."""

    agent: str
    phase: str
    start: float
    end: float
    status: str = "ok"

    @property
    def duration_ms(self) -> float:
        return max(0.0, (self.end - self.start) * 1000.0)

    @property
    def round_num(self) -> int | None:
        """Round number when ``phase`` is ``round_N``; ``None`` otherwise."""
        if self.phase.startswith("round_"):
            try:
                return int(self.phase.split("_", 1)[1])
            except ValueError:
                return None
        return None


@dataclass
class RunTrace:
    """Collection of spans for a single council run."""

    spans: list[Span] = field(default_factory=list)

    def add_span(
        self, agent: str, phase: str, start: float, end: float, status: str = "ok"
    ) -> Span:
        span = Span(agent=agent, phase=phase, start=start, end=end, status=status)
        self.spans.append(span)
        return span

    def to_dict(self) -> dict[str, Any]:
        return {"spans": [asdict(s) for s in self.spans]}

    def write(self, path: Path) -> Path:
        """Write the trace to *path* (creating parents). Never raises."""
        try:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(json.dumps(self.to_dict(), indent=2), encoding="utf-8")
        except OSError as exc:  # pragma: no cover - defensive
            logger.warning("Could not write trace %s: %s", path, exc)
        return path

    @classmethod
    def load(cls, path: Path) -> RunTrace:
        """Load a trace from *path*; returns an empty trace on any error."""
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            return cls()
        spans = [
            Span(
                agent=s.get("agent", ""),
                phase=s.get("phase", ""),
                start=float(s.get("start", 0.0)),
                end=float(s.get("end", 0.0)),
                status=s.get("status", "ok"),
            )
            for s in data.get("spans", [])
        ]
        return cls(spans=spans)

    def export_otel(self, service_name: str = "council") -> bool:
        """Emit spans via OpenTelemetry if available; return True when exported.

        Best-effort: returns False (no-op) when the OTel SDK is not installed.
        """
        try:
            from opentelemetry import trace as ot_trace
            from opentelemetry.sdk.trace import TracerProvider
        except ImportError:
            logger.debug("OpenTelemetry not installed; skipping OTel export")
            return False

        provider = ot_trace.get_tracer_provider()
        if not isinstance(provider, TracerProvider):  # pragma: no cover - env dependent
            ot_trace.set_tracer_provider(TracerProvider())
        tracer = ot_trace.get_tracer(service_name)
        for span in self.spans:
            otel_span = tracer.start_span(
                f"{span.agent}:{span.phase}",
                start_time=int(span.start * 1e9),
            )
            otel_span.set_attribute("agent", span.agent)
            otel_span.set_attribute("phase", span.phase)
            otel_span.set_attribute("status", span.status)
            otel_span.end(end_time=int(span.end * 1e9))
        return True


__all__ = ["TRACE_FILENAME", "RunTrace", "Span"]
