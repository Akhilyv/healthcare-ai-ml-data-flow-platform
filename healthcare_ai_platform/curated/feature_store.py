from typing import Any, Dict
from healthcare_ai_platform.curated.bigquery_repository import BigQueryRepository
class FeatureStore:
    def __init__(self, repo: BigQueryRepository | None = None): self.repo=repo or BigQueryRepository()
    def get_readmission_features(self, patient_id: str) -> Dict[str, Any]: return self.repo._read().get("risk_features",{}).get(patient_id,{"prior_admission_count":0,"abnormal_lab_count":0,"medication_count":0,"comorbidity_count":0})
    def save_feature_vector(self, patient_id: str, features: Dict[str, Any]) -> None: self.repo.save_risk_features(patient_id, features)
    def get_patient_risk_features(self, patient_id: str) -> Dict[str, Any]: return self.get_readmission_features(patient_id)
