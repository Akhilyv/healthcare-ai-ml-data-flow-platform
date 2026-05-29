from typing import Any, Dict
from healthcare_ai_platform.curated.bigquery_repository import BigQueryRepository
class EHRIngestionService:
    def __init__(self, repo: BigQueryRepository | None = None): self.repo=repo or BigQueryRepository()
    def ingest_encounter(self, patient_id: str, encounter: Dict[str, Any]): self.repo.save_patient_context(patient_id,{"latest_encounter":encounter}); return {"status":"stored","source_system":"mock_ehr"}
    def ingest_lab_result(self, patient_id: str, lab: Dict[str, Any]): self.repo.save_patient_context(patient_id,{"latest_lab":lab}); return {"status":"stored","source_system":"mock_ehr"}
    def ingest_diagnosis(self, patient_id: str, diagnosis: Dict[str, Any]): self.repo.save_patient_context(patient_id,{"latest_diagnosis":diagnosis}); return {"status":"stored","source_system":"mock_ehr"}
    def ingest_medication(self, patient_id: str, medication: Dict[str, Any]): self.repo.save_patient_context(patient_id,{"latest_medication":medication}); return {"status":"stored","source_system":"mock_ehr"}
    def ingest_clinical_note(self, patient_id: str, note: Dict[str, Any]): self.repo.save_clinical_document({"patient_id":patient_id, **note}); return {"status":"stored","source_system":"mock_ehr"}
