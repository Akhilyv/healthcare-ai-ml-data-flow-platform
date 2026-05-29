from typing import Any, Dict, List, TypedDict
class ClinicalDecisionState(TypedDict, total=False):
    request: Dict[str, Any]; user_context: Dict[str, Any]; patient_context: Dict[str, Any]; retrieved_context: List[Dict[str, Any]]; nlp_signals: Dict[str, Any]; risk_scores: Dict[str, Any]; draft_answer: str; validation_result: Dict[str, Any]; governance_flags: List[str]; human_review_required: bool; final_answer: str; audit_id: str; access_denied: bool
