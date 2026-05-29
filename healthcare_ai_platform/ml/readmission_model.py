from pathlib import Path
from typing import Any, Dict

from healthcare_ai_platform.core.settings import settings


class ReadmissionRiskModel:
    model_version = "deterministic-baseline-0.1-not-clinically-validated"
    feature_order = [
        "prior_admission_count",
        "days_since_last_discharge",
        "abnormal_lab_count",
        "medication_count",
        "comorbidity_count",
        "has_follow_up_gap",
        "has_transportation_barrier",
        "has_medication_adherence_issue",
        "diagnosis_count",
        "high_risk_condition_count",
    ]

    def __init__(self, model_path: str | None = None):
        self.model_path = model_path or settings.readmission_model_path
        self.model = self._load_optional_model(self.model_path)

    def _load_optional_model(self, model_path: str | None):
        if not model_path or not Path(model_path).exists():
            return None
        try:
            import joblib

            self.model_version = f"sklearn-artifact:{Path(model_path).name}-not-clinically-validated"
            return joblib.load(model_path)
        except Exception:
            self.model_version = "deterministic-baseline-0.1-not-clinically-validated"
            return None

    def _feature_row(self, features: Dict[str, Any]):
        row = []
        for key in self.feature_order:
            value = features.get(key, 0)
            if isinstance(value, bool):
                row.append(1.0 if value else 0.0)
            elif isinstance(value, (int, float)):
                row.append(float(value))
            else:
                row.append(0.0)
        return row

    def _predict_with_artifact(self, features: Dict[str, Any]) -> Dict[str, Any] | None:
        if self.model is None:
            return None
        try:
            row = [self._feature_row(features)]
            if hasattr(self.model, "predict_proba"):
                score = float(self.model.predict_proba(row)[0][-1])
            else:
                score = float(self.model.predict(row)[0])
            score = max(0.0, min(1.0, score))
            level = "high" if score >= 0.65 else "medium" if score >= 0.35 else "low"
            return {
                "readmission_risk": round(score, 3),
                "risk_level": level,
                "top_factors": [],
                "model_version": self.model_version,
                "validated": False,
            }
        except Exception:
            return None

    def _baseline_predict(self, features: Dict[str, Any]) -> Dict[str, Any]:
        weights = {
            "prior_admission_count": 0.07,
            "abnormal_lab_count": 0.08,
            "medication_count": 0.02,
            "comorbidity_count": 0.06,
            "has_follow_up_gap": 0.15,
            "has_transportation_barrier": 0.10,
            "has_medication_adherence_issue": 0.14,
            "diagnosis_count": 0.03,
            "high_risk_condition_count": 0.10,
        }
        score = 0.05
        contributions = []
        for key, weight in weights.items():
            raw = features.get(key, 0)
            value = 1 if isinstance(raw, bool) and raw else raw if isinstance(raw, (int, float)) else 0
            contribution = min(float(value) * weight, 0.25)
            score += contribution
            if contribution > 0:
                contributions.append({"factor": key, "contribution": round(contribution, 3), "value": raw})
        score = max(0.0, min(1.0, score))
        level = "high" if score >= 0.65 else "medium" if score >= 0.35 else "low"
        return {
            "readmission_risk": round(score, 3),
            "risk_level": level,
            "top_factors": sorted(contributions, key=lambda x: x["contribution"], reverse=True)[:5],
            "model_version": self.model_version,
            "validated": False,
        }

    def predict(self, features: Dict[str, Any]) -> Dict[str, Any]:
        return self._predict_with_artifact(features) or self._baseline_predict(features)
