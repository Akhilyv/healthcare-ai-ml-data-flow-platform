from typing import Any, Dict
class ClaimsIngestionService:
    def normalize_claim(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        keys=["claim_id","patient_id","encounter_id","diagnosis_codes","procedure_codes","payer","amount","status"]
        out={k:payload.get(k) for k in keys}; out["diagnosis_codes"]=out.get("diagnosis_codes") or []; out["procedure_codes"]=out.get("procedure_codes") or []; return out
