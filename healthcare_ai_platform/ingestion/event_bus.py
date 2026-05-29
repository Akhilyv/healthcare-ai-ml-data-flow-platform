from collections import defaultdict
from datetime import datetime, timezone
from typing import Any, Callable, Dict, List
from uuid import uuid4


class LocalClinicalEventBus:
    """Pub/Sub-style in-memory event bus for local development and tests."""

    def __init__(self):
        self.events: List[Dict[str, Any]] = []
        self.subscribers: Dict[str, List[Callable[[Dict[str, Any]], None]]] = defaultdict(list)

    def publish(self, topic: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        event = {
            "event_id": str(uuid4()),
            "topic": topic,
            "payload": payload,
            "published_at": datetime.now(timezone.utc).isoformat(),
        }
        self.events.append(event)
        for handler in self.subscribers.get(topic, []):
            handler(event)
        return event

    def subscribe(self, topic: str, handler: Callable[[Dict[str, Any]], None]) -> None:
        self.subscribers[topic].append(handler)


event_bus = LocalClinicalEventBus()
