from typing import Any, Dict, List
class SourceCitationService:
    def build_citations(self, chunks: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        return [{"id": c.get("id", f"C{i}"), "source": c.get("source", "curated_context"), "title": c.get("title", c.get("document_type", "clinical context")), "snippet": c.get("content", "")[:240]} for i,c in enumerate(chunks,1)]
    def validate_answer_grounding(self, answer: str, citations: List[Dict[str, Any]]) -> Dict[str, Any]:
        insufficient="evidence is insufficient" in (answer or "").lower(); grounded=bool(citations) or insufficient; return {"grounded": grounded, "flags": [] if grounded else ["ungrounded_answer"]}
    def detect_unsupported_claims(self, answer: str, retrieved_context: List[Dict[str, Any]]) -> List[str]:
        if "unsupported diagnosis" in (answer or "").lower(): return ["unsupported_diagnosis_claim"]
        if not retrieved_context and "evidence is insufficient" not in (answer or "").lower(): return ["no_retrieved_evidence"]
        return []
