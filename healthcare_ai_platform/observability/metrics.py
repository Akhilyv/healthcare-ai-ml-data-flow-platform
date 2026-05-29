from collections import defaultdict
from typing import Dict


CLINICAL_REQUESTS_TOTAL = "clinical_requests_total"
RAG_RETRIEVAL_LATENCY_MS = "rag_retrieval_latency_ms"
LLM_LATENCY_MS = "llm_latency_ms"
RISK_MODEL_LATENCY_MS = "risk_model_latency_ms"
GUARDRAIL_FAILURES_TOTAL = "guardrail_failures_total"
HUMAN_REVIEW_REQUIRED_TOTAL = "human_review_required_total"
UNSUPPORTED_CLAIMS_TOTAL = "unsupported_claims_total"
PHI_REDACTION_EVENTS_TOTAL = "phi_redaction_events_total"


class MetricsRegistry:
    def __init__(self):
        self.counters = defaultdict(int)
        self.gauges = {}

    def increment(self, name: str, value: int = 1):
        self.counters[name] += value

    def set_gauge(self, name: str, value: float):
        self.gauges[name] = value

    def snapshot(self) -> Dict:
        return {"counters": dict(self.counters), "gauges": dict(self.gauges)}


metrics = MetricsRegistry()
