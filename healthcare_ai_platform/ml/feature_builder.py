from typing import Any, Dict
class ReadmissionFeatureBuilder:
    HIGH_RISK={"heart failure","chronic kidney disease","diabetes mellitus"}
    def build(self, patient_context: Dict[str, Any]) -> Dict[str, Any]:
        entities=[i.get("entities",{}) for i in patient_context.get("entities",[])]
        conditions=[c for e in entities for c in e.get("conditions",[])]; meds=[m for e in entities for m in e.get("medications",[])]; labs=[l for e in entities for l in e.get("labs",[])]; social=[s for e in entities for s in e.get("social_risks",[])]; adherence=[a for e in entities for a in e.get("adherence_risks",[])]
        return {"prior_admission_count":patient_context.get("prior_admission_count",0),"days_since_last_discharge":patient_context.get("days_since_last_discharge",999),"abnormal_lab_count":sum(1 for l in labs if l.get("abnormal")),"medication_count":len(set(meds)),"comorbidity_count":len(set(conditions)),"has_follow_up_gap":bool(patient_context.get("has_follow_up_gap",False)),"has_transportation_barrier":"transportation barrier" in social,"has_medication_adherence_issue":bool(adherence),"age_bucket":patient_context.get("age_bucket","unknown"),"diagnosis_count":len(set(conditions)),"high_risk_condition_count":sum(1 for c in set(conditions) if c in self.HIGH_RISK)}
