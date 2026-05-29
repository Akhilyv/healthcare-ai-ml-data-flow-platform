from typing import Any, Dict, List, Optional
from pydantic import BaseModel, ConfigDict, Field, StrictBool, StrictFloat, StrictStr


class StrictSchema(BaseModel):
    model_config = ConfigDict(strict=True)


class ClinicalDocumentInput(StrictSchema):
    patient_id: StrictStr
    encounter_id: StrictStr
    facility_id: StrictStr
    document_type: StrictStr
    text: StrictStr
    metadata: Dict[str, Any] = Field(default_factory=dict)


class FHIRResourceInput(StrictSchema):
    resource_type: StrictStr
    resource_id: StrictStr
    patient_id: StrictStr
    payload: Dict[str, Any]


class HL7v2MessageInput(StrictSchema):
    message_type: StrictStr
    facility_id: StrictStr
    raw_message: StrictStr


class ClinicalQueryRequest(StrictSchema):
    user_id: StrictStr
    role: StrictStr
    patient_id: StrictStr
    encounter_id: Optional[StrictStr] = None
    facility_id: StrictStr
    question: StrictStr
    include_risk_score: StrictBool = True
    require_human_review: StrictBool = True


class ClinicalSummaryResponse(StrictSchema):
    patient_id: StrictStr
    encounter_id: Optional[StrictStr] = None
    answer: StrictStr
    retrieved_context: List[Dict[str, Any]]
    citations: List[Dict[str, Any]]
    risk_scores: Dict[str, Any]
    governance_flags: List[StrictStr]
    requires_human_review: StrictBool
    audit_id: StrictStr


class RiskScoreResponse(StrictSchema):
    patient_id: StrictStr
    readmission_risk: StrictFloat
    risk_level: StrictStr
    top_factors: List[Dict[str, Any]]
    model_version: StrictStr
    disclaimer: StrictStr


class RAGEvaluationRequest(StrictSchema):
    answer: StrictStr
    retrieved_context: List[Dict[str, Any]]
    citations: List[Dict[str, Any]]


class DashboardExportResponse(StrictSchema):
    json_path: StrictStr
    csv_path: StrictStr
    summary: Dict[str, Any]
