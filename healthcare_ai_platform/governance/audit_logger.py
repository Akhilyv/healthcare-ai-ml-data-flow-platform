import json, uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from healthcare_ai_platform.core.settings import settings

class AuditLogger:
    def __init__(self, path: str | None = None):
        self.path = Path(path or settings.audit_log_path)
        self.path.parent.mkdir(parents=True, exist_ok=True)

    def start(self, **fields: Any) -> str:
        audit_id = str(uuid.uuid4())
        self.log(audit_id=audit_id, event="start", **fields)
        return audit_id

    def log(self, **record: Any) -> None:
        record.setdefault("timestamp", datetime.now(timezone.utc).isoformat())
        with self.path.open("a", encoding="utf-8") as f:
            f.write(json.dumps(record, default=str) + "\n")
