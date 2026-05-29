from typing import Any, Dict, List
from healthcare_ai_platform.governance.guardrails import DECISION_SUPPORT_DISCLAIMER

class ClinicalPromptBuilder:
    def _facts(self, retrieved: List[Dict[str, Any]]) -> str:
        return "\n".join(f"- [{c.get('id')}] {c.get('content', '')}" for c in retrieved)

    def clinical_summary(self, question: str, retrieved: List[Dict[str, Any]], citations: List[Dict[str, Any]]) -> str:
        return (
            "System: Healthcare decision support. Avoid unsupported claims. Say evidence is insufficient when needed. "
            "Keep clinician in control.\n"
            f"Question: {question}\nFacts:\n{self._facts(retrieved)}\nCitations: {citations}\n{DECISION_SUPPORT_DISCLAIMER}"
        )

    def retrieved_context_answer(self, question, retrieved, citations):
        return self.clinical_summary(question, retrieved, citations)

    def readmission_support(self, risk: Dict[str, Any]) -> str:
        return f"Explain readmission support score transparently: {risk}. {DECISION_SUPPORT_DISCLAIMER}"

    def risk_explanation(self, risk: Dict[str, Any]) -> str:
        return self.readmission_support(risk)

    def human_review_package(self, answer: str, citations: List[Dict[str, Any]]) -> str:
        return f"Clinician review package\nAnswer: {answer}\nEvidence: {citations}"
