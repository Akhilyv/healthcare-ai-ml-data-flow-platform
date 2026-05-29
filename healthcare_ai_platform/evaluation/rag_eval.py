from typing import Any, Dict, List


class RAGEvaluator:
    def __init__(self):
        self.ragas_available = self._detect_ragas()

    def _detect_ragas(self) -> bool:
        try:
            import ragas  # noqa: F401

            return True
        except Exception:
            return False

    def evaluate(self, answer: str, retrieved_context: List[Dict[str, Any]], citations: List[Dict[str, Any]]) -> Dict[str, Any]:
        unsupported = 0 if retrieved_context or "evidence is insufficient" in (answer or "").lower() else 1
        citation_coverage = min(1.0, len(citations) / max(len(retrieved_context), 1))
        result = {
            "context_relevance": min(1.0, len(retrieved_context) / 3),
            "groundedness": 1.0 if unsupported == 0 else 0.0,
            "answer_faithfulness": 1.0 if unsupported == 0 else 0.0,
            "citation_coverage": citation_coverage,
            "unsupported_claim_count": unsupported,
            "retrieval_count": len(retrieved_context),
            "engine": "ragas_optional_hook" if self.ragas_available else "heuristic",
        }
        if self.ragas_available:
            result["ragas_status"] = "available_not_executed_without_dataset"
        return result
