import re
from typing import Any, Dict, List
from healthcare_ai_platform.nlp.note_sectionizer import NoteSectionizer

class ClinicalNLPService:
    def __init__(self): self.sectionizer = NoteSectionizer()
    def sectionize_note(self, text: str) -> Dict[str, str]: return self.sectionizer.sectionize(text)
    def _find_terms(self, text: str, terms: Dict[str, str]) -> List[str]: return sorted({label for pattern, label in terms.items() if re.search(pattern, text or "", re.I)})
    def extract_conditions(self, text: str) -> List[str]: return self._find_terms(text, {r"\bCHF\b|heart failure": "heart failure", r"\bCKD\b|chronic kidney": "chronic kidney disease", r"diabetes|\bDM\b": "diabetes mellitus", r"hypertension|\bHTN\b": "hypertension"})
    def extract_medications(self, text: str) -> List[str]: return sorted({m.lower() for m in re.findall(r"\b(?:metformin|lisinopril|furosemide|insulin|atorvastatin|warfarin|apixaban)\b", text or "", re.I)})
    def extract_lab_mentions(self, text: str) -> List[Dict[str, Any]]:
        labs = []
        for name in ["creatinine", "A1C", "hemoglobin", "potassium", "BNP"]:
            for match in re.finditer(rf"\b{name}\b\s*(?:is|=|:)?\s*(\d+(?:\.\d+)?)?", text or "", re.I):
                value = match.group(1); abnormal = False
                if value:
                    v = float(value); abnormal = (name.lower()=="creatinine" and v>1.3) or (name.lower()=="a1c" and v>7.0) or (name.lower()=="potassium" and (v<3.5 or v>5.2))
                labs.append({"name": name, "value": value, "abnormal": abnormal})
        return labs
    def extract_follow_up_instructions(self, text: str) -> List[str]: return [h.strip() for h in re.findall(r"follow[- ]?up[^.\n]*(?:within\s+\d+\s+days|\d+\s+days|one week|7 days)?", text or "", re.I)]
    def extract_social_risk_factors(self, text: str) -> List[str]: return self._find_terms(text, {r"transportation": "transportation barrier", r"lives alone": "lives alone", r"food insecurity": "food insecurity", r"housing instability|homeless": "housing instability"})
    def extract_adherence_risks(self, text: str) -> List[str]: return self._find_terms(text, {r"non[- ]adherence|noncompliance|missed medications|cannot afford": "medication adherence risk"})
    def classify_risk_signals(self, text: str) -> List[str]:
        signals = []
        if self.extract_adherence_risks(text): signals.append("adherence_risk")
        if self.extract_social_risk_factors(text): signals.append("social_risk")
        if re.search(r"readmission|discharge risk|high risk", text or "", re.I): signals.append("discharge_risk")
        if any(l["abnormal"] for l in self.extract_lab_mentions(text)): signals.append("abnormal_labs")
        return signals
    def extract_entities(self, text: str) -> Dict[str, Any]:
        return {"conditions": self.extract_conditions(text), "medications": self.extract_medications(text), "labs": self.extract_lab_mentions(text), "follow_up": self.extract_follow_up_instructions(text), "social_risks": self.extract_social_risk_factors(text), "adherence_risks": self.extract_adherence_risks(text), "risk_signals": self.classify_risk_signals(text), "sections": self.sectionize_note(text)}
