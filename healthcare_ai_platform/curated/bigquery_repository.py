import json
from pathlib import Path
from typing import Any, Dict, List
from healthcare_ai_platform.core.settings import settings

class BigQueryRepository:
    def __init__(self, local_path: str | None = None):
        self.path = Path(local_path or settings.local_curated_path); self.path.parent.mkdir(parents=True, exist_ok=True)
        if not self.path.exists(): self._write({"patient_context": {}, "documents": [], "entities": [], "risk_features": {}})
    def _read(self) -> Dict[str, Any]: return json.loads(self.path.read_text(encoding="utf-8"))
    def _write(self, data: Dict[str, Any]) -> None: self.path.write_text(json.dumps(data, indent=2), encoding="utf-8")
    def save_patient_context(self, patient_id: str, context: Dict[str, Any]) -> None:
        data=self._read(); data["patient_context"][patient_id]={**data["patient_context"].get(patient_id,{}), **context}; self._write(data)
    def save_clinical_document(self, document: Dict[str, Any]) -> None:
        data=self._read(); data["documents"].append(document); self._write(data)
    def save_extracted_entities(self, patient_id: str, encounter_id: str, entities: Dict[str, Any]) -> None:
        data=self._read(); data["entities"].append({"patient_id": patient_id, "encounter_id": encounter_id, "entities": entities}); self._write(data)
    def save_risk_features(self, patient_id: str, features: Dict[str, Any]) -> None:
        data=self._read(); data["risk_features"][patient_id]=features; self._write(data)
    def get_patient_context(self, patient_id: str) -> Dict[str, Any]:
        data=self._read(); docs=[d for d in data["documents"] if d.get("patient_id")==patient_id]; ents=[e for e in data["entities"] if e.get("patient_id")==patient_id]
        context=data["patient_context"].get(patient_id,{}).copy(); context.update({"documents": docs, "entities": ents}); return context
    def get_encounter_context(self, patient_id: str, encounter_id: str) -> Dict[str, Any]:
        c=self.get_patient_context(patient_id); c["documents"]=[d for d in c.get("documents",[]) if d.get("encounter_id")==encounter_id]; return c
    def get_recent_labs(self, patient_id: str) -> List[Dict[str, Any]]:
        labs=[]
        for item in self.get_patient_context(patient_id).get("entities",[]): labs.extend(item.get("entities",{}).get("labs",[]))
        return labs
    def get_diagnosis_history(self, patient_id: str) -> List[str]:
        vals=[]
        for item in self.get_patient_context(patient_id).get("entities",[]): vals.extend(item.get("entities",{}).get("conditions",[]))
        return sorted(set(vals))
    def get_medication_history(self, patient_id: str) -> List[str]:
        vals=[]
        for item in self.get_patient_context(patient_id).get("entities",[]): vals.extend(item.get("entities",{}).get("medications",[]))
        return sorted(set(vals))
    def get_note_metadata(self, patient_id: str) -> List[Dict[str, Any]]: return [{"encounter_id": d.get("encounter_id"), "document_type": d.get("document_type"), "metadata": d.get("metadata",{})} for d in self.get_patient_context(patient_id).get("documents",[])]

    def list_clinical_documents(self) -> List[Dict[str, Any]]:
        return self._read().get("documents", [])

    def list_dashboard_records(self) -> List[Dict[str, Any]]:
        data = self._read()
        records = []
        for document in data.get("documents", []):
            records.append({
                "facility_id": document.get("facility_id", "unknown"),
                "document_type": document.get("document_type", "unknown"),
                "requires_human_review": True,
                "retrieval_count": 0,
                "guardrail_flags": document.get("phi_findings_preview", []),
                "risk_level": "unknown",
            })
        for patient_id, features in data.get("risk_features", {}).items():
            records.append({
                "patient_id": patient_id,
                "facility_id": "unknown",
                "document_type": "risk_features",
                "requires_human_review": True,
                "retrieval_count": 0,
                "guardrail_flags": [],
                "risk_level": features.get("risk_level", "unknown"),
            })
        return records
