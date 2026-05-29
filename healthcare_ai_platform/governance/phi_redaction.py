import re
from typing import Any, Dict, List, Tuple

class PHIRedactor:
    def __init__(self, redact_dates: bool = False):
        self.patterns: List[Tuple[str, str]] = [
            ("email", r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b"),
            ("phone", r"\b(?:\+?1[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}\b"),
            ("ssn", r"\b\d{3}-\d{2}-\d{4}\b"),
            ("mrn", r"\b(?:MRN|Medical Record Number)[:#\s-]*[A-Z0-9-]{5,}\b"),
            ("address", r"\b\d{2,5}\s+[A-Za-z0-9 .]+\s(?:Street|St|Avenue|Ave|Road|Rd|Drive|Dr|Lane|Ln)\b"),
        ]
        if redact_dates:
            self.patterns.append(("date", r"\b\d{1,2}/\d{1,2}/\d{2,4}\b"))

    def detect_phi(self, text: str) -> List[Dict[str, str]]:
        findings = []
        for label, pattern in self.patterns:
            for match in re.finditer(pattern, text or "", re.IGNORECASE):
                findings.append({"type": label, "value": match.group(0)})
        return findings

    def redact_text(self, text: str, metadata: Dict[str, Any] | None = None) -> str:
        redacted = text or ""
        for label, pattern in self.patterns:
            redacted = re.sub(pattern, f"[{label.upper()}_REDACTED]", redacted, flags=re.IGNORECASE)
        for name in (metadata or {}).get("patient_names", []) or []:
            redacted = re.sub(re.escape(str(name)), "[PATIENT_NAME_REDACTED]", redacted, flags=re.IGNORECASE)
        return redacted

    def redact_payload(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        def redact(value: Any) -> Any:
            if isinstance(value, str): return self.redact_text(value)
            if isinstance(value, dict): return {k: redact(v) for k, v in value.items()}
            if isinstance(value, list): return [redact(v) for v in value]
            return value
        return redact(payload)
