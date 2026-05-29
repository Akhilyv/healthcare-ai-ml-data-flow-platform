from dataclasses import dataclass
from typing import Dict, Tuple

@dataclass(frozen=True)
class RBACDecision:
    allowed: bool
    reason: str
    deidentified_only: bool = False

class RBACPolicy:
    matrix: Dict[str, Dict[str, bool]] = {
        "physician": {"full_phi": True, "risk": True, "audit": False},
        "nurse": {"full_phi": True, "risk": True, "audit": False},
        "care_manager": {"full_phi": False, "risk": True, "audit": False},
        "analyst": {"full_phi": False, "risk": False, "audit": False},
        "admin": {"full_phi": False, "risk": False, "audit": True},
    }
    def authorize(self, role: str, action: str, patient_id: str | None = None) -> RBACDecision:
        normalized = (role or "").lower()
        if normalized not in self.matrix: return RBACDecision(False, f"Unknown role: {role}")
        if action == "patient_context":
            if self.matrix[normalized]["full_phi"]: return RBACDecision(True, "Full clinical context permitted")
            if normalized == "care_manager": return RBACDecision(True, "Limited discharge and risk-factor context permitted", True)
            return RBACDecision(False, "Role is limited to de-identified or administrative data", True)
        if action == "risk_score": return RBACDecision(self.matrix[normalized]["risk"], "Risk access policy evaluated", not self.matrix[normalized]["risk"])
        if action == "audit": return RBACDecision(self.matrix[normalized]["audit"], "Audit access policy evaluated")
        return RBACDecision(True, "Action permitted")
    def can_access_patient_context(self, role: str, patient_id: str) -> Tuple[bool, str]:
        d = self.authorize(role, "patient_context", patient_id); return d.allowed, d.reason
