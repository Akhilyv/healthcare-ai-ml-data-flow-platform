from typing import Any, Dict, List
class HumanReviewService:
    def mark_requires_review(self, reason: str, flags: List[str] | None = None) -> Dict[str, Any]: return {"requires_human_review": True, "reason": reason, "flags": flags or []}
    def create_review_package(self, request: Dict[str, Any], answer: str, evidence: List[Dict[str, Any]], flags: List[str]) -> Dict[str, Any]: return {"request": request, "draft_answer": answer, "evidence": evidence, "flags": flags, "reviewer_instructions": "Clinician must verify evidence, risk score, and final wording before patient-care use."}
    def approve_output(self, audit_id: str, reviewer_id: str) -> Dict[str, str]: return {"audit_id": audit_id, "reviewer_id": reviewer_id, "status": "approved"}
    def reject_output(self, audit_id: str, reviewer_id: str, reason: str) -> Dict[str, str]: return {"audit_id": audit_id, "reviewer_id": reviewer_id, "status": "rejected", "reason": reason}
