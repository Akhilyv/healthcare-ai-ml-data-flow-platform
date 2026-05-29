import time
from contextlib import contextmanager
from typing import Any, Dict, List


class Tracer:
    def __init__(self):
        self.events: List[Dict[str, Any]] = []

    def start_span(self, name: str):
        self.events.append({"event": "span_start", "name": name, "ts": time.time(), "workflow.node.name": name})

    def end_span(self, name: str):
        self.events.append({"event": "span_end", "name": name, "ts": time.time()})

    def log_event(self, name: str, attributes=None):
        self.events.append({"event": name, "attributes": attributes or {}, "ts": time.time()})

    @contextmanager
    def span(self, name: str, attributes: Dict[str, Any] | None = None):
        self.start_span(name)
        if attributes:
            self.log_event("workflow.node.attributes", attributes)
        try:
            yield
        finally:
            self.end_span(name)


tracer = Tracer()
