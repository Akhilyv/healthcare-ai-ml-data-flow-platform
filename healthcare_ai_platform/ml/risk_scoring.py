from typing import Any, Dict
from healthcare_ai_platform.curated.bigquery_repository import BigQueryRepository
from healthcare_ai_platform.ml.feature_builder import ReadmissionFeatureBuilder
from healthcare_ai_platform.ml.readmission_model import ReadmissionRiskModel
class RiskScoringService:
    def __init__(self, repo: BigQueryRepository | None = None): self.repo=repo or BigQueryRepository(); self.builder=ReadmissionFeatureBuilder(); self.model=ReadmissionRiskModel()
    def calculate_patient_risk(self, patient_id: str) -> Dict[str, Any]:
        features=self.builder.build(self.repo.get_patient_context(patient_id)); self.repo.save_risk_features(patient_id,features); return self.model.predict(features)
    def explain_risk_score(self, result: Dict[str, Any]) -> str: return "Risk score is decision support only and not clinically validated. Top factors: " + ", ".join(f["factor"] for f in result.get("top_factors",[]))
    def validate_risk_output(self, result: Dict[str, Any]) -> bool: return 0 <= result.get("readmission_risk",-1) <= 1 and result.get("risk_level") in {"low","medium","high"}
