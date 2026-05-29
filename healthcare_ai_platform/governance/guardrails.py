import re
from typing import Dict, List
from healthcare_ai_platform.governance.phi_redaction import PHIRedactor

DECISION_SUPPORT_DISCLAIMER = "This output is for clinical decision support and requires clinician review."

class ClinicalGuardrails:
    def __init__(self):
        self.redactor = PHIRedactor()

    def validate_query(self, question: str) -> List[str]:
        lowered = (question or "").lower()
        flags = []
        if any(t in lowered for t in ["ignore previous", "system prompt", "developer message", "jailbreak"]):
            flags.append("prompt_injection_risk")
        if any(t in lowered for t in ["guarantee diagnosis", "replace doctor", "definitive treatment"]):
            flags.append("unsafe_medical_framing")
        return flags

    def check_output(self, answer: str, citations: List[Dict] | None = None) -> List[str]:
        flags = []
        text = answer or ""
        if DECISION_SUPPORT_DISCLAIMER not in text:
            flags.append("missing_decision_support_disclaimer")
        if citations is not None and len(citations) == 0 and "evidence is insufficient" not in text.lower():
            flags.append("missing_citation")
        if self.redactor.detect_phi(text):
            flags.append("phi_exposure")
        if re.search(r"\b(start|stop|increase|decrease)\s+\w+\s+(?:medication|dose|mg)\b", text, re.I):
            flags.append("unsafe_medical_advice")
        if re.search(r"\b(chest pain|stroke symptoms|suicidal|severe shortness of breath)\b", text, re.I) and not re.search(r"\b(emergency|911|urgent|escalat)\b", text, re.I):
            flags.append("missing_emergency_escalation_language")
        return flags

    def add_disclaimer(self, answer: str) -> str:
        return answer if DECISION_SUPPORT_DISCLAIMER in answer else f"{answer}\n\n{DECISION_SUPPORT_DISCLAIMER}"
