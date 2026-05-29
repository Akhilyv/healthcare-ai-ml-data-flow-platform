from typing import Any, Dict
class FHIRIngestionService:
    SUPPORTED={"Patient","Encounter","Observation","Condition","DiagnosticReport","MedicationRequest"}
    def validate_resource(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        rt=payload.get("resourceType"); return {"valid": rt in self.SUPPORTED and bool(payload.get("id")), "resource_type": rt, "errors": [] if rt in self.SUPPORTED else ["unsupported_resource_type"]}
    def normalize_patient(self,p): return {"patient_id": p.get("id"), "resource_type":"Patient", "name":p.get("name",[])}
    def normalize_encounter(self,p): return {"encounter_id":p.get("id"), "patient_ref":p.get("subject",{}).get("reference"), "status":p.get("status")}
    def normalize_observation(self,p): return {"observation_id":p.get("id"), "code":p.get("code",{}), "value":p.get("valueQuantity") or p.get("valueString")}
    def normalize_condition(self,p): return {"condition_id":p.get("id"), "code":p.get("code",{}), "clinical_status":p.get("clinicalStatus",{})}
    def normalize_medication_request(self,p): return {"medication_request_id":p.get("id"), "medication":p.get("medicationCodeableConcept",{}), "status":p.get("status")}
    def normalize(self,p):
        return {"Patient":self.normalize_patient,"Encounter":self.normalize_encounter,"Observation":self.normalize_observation,"Condition":self.normalize_condition,"DiagnosticReport":lambda x:{"diagnostic_report_id":x.get("id"),"code":x.get("code",{}),"result":x.get("result",[])},"MedicationRequest":self.normalize_medication_request}.get(p.get("resourceType"), lambda x:x)(p)
