def evaluate_summary_completeness(answer: str) -> dict: return {"complete": bool(answer and "decision support" in answer.lower())}
def evaluate_risk_explanation(risk: dict) -> dict: return {"has_top_factors": bool(risk.get("top_factors")), "valid_range": 0 <= risk.get("readmission_risk", 0) <= 1}
def evaluate_safety_flags(flags: list) -> dict: return {"flag_count": len(flags), "critical": [f for f in flags if f in {"phi_exposure", "unsafe_medical_advice"}]}
def evaluate_human_review_routing(required: bool, flags: list) -> dict: return {"appropriate": required or not flags}
