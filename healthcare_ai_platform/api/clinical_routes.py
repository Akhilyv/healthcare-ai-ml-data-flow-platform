from fastapi import APIRouter, HTTPException

from healthcare_ai_platform.api.schemas import (
    ClinicalDocumentInput,
    ClinicalQueryRequest,
    ClinicalSummaryResponse,
    DashboardExportResponse,
    FHIRResourceInput,
    HL7v2MessageInput,
    RAGEvaluationRequest,
    RiskScoreResponse,
)
from healthcare_ai_platform.curated.bigquery_repository import BigQueryRepository
from healthcare_ai_platform.dashboards.dashboard_export import DashboardExporter
from healthcare_ai_platform.evaluation.rag_eval import RAGEvaluator
from healthcare_ai_platform.governance.audit_logger import AuditLogger
from healthcare_ai_platform.governance.guardrails import ClinicalGuardrails
from healthcare_ai_platform.governance.phi_redaction import PHIRedactor
from healthcare_ai_platform.ingestion.dataflow_transformer import ClinicalDataflowTransformer
from healthcare_ai_platform.ingestion.event_bus import event_bus
from healthcare_ai_platform.ingestion.fhir_ingestion import FHIRIngestionService
from healthcare_ai_platform.ingestion.hl7v2_ingestion import HL7v2IngestionService
from healthcare_ai_platform.ml.risk_scoring import RiskScoringService
from healthcare_ai_platform.nlp.clinical_nlp import ClinicalNLPService
from healthcare_ai_platform.observability.metrics import PHI_REDACTION_EVENTS_TOTAL, metrics
from healthcare_ai_platform.workflows.clinical_decision_graph import build_clinical_decision_graph

DECISION_SUPPORT_RISK_DISCLAIMER = (
    "This readmission score is decision support only, is not clinically validated, "
    "and must not be used as a final diagnosis or treatment decision."
)

router = APIRouter(prefix="/v2/clinical", tags=["clinical-platform"])
repo = BigQueryRepository()
redactor = PHIRedactor()
nlp = ClinicalNLPService()
audit = AuditLogger()
guardrails = ClinicalGuardrails()
transformer = ClinicalDataflowTransformer()


@router.post("/documents/ingest")
def ingest_document(document: ClinicalDocumentInput):
    audit_id = audit.start(
        user_id="system",
        role="ingestion",
        patient_id=document.patient_id,
        facility_id=document.facility_id,
        route="/v2/clinical/documents/ingest",
    )
    findings = redactor.detect_phi(document.text)
    if findings:
        metrics.increment(PHI_REDACTION_EVENTS_TOTAL, len(findings))
    redacted = redactor.redact_text(document.text, document.metadata)
    entities = nlp.extract_entities(redacted)

    record = document.model_dump()
    record["redacted_text"] = redacted
    record["phi_findings_preview"] = [finding["type"] for finding in findings]
    event = event_bus.publish("clinical.document.ingested", record)
    transformed = transformer.transform_patient_context_event(event)
    repo.save_clinical_document(record)
    repo.save_extracted_entities(document.patient_id, document.encounter_id, entities)
    audit.log(
        audit_id=audit_id,
        event="document_ingested",
        entity_groups=list(entities.keys()),
        phi_findings=len(findings),
    )
    return {
        "status": "ingested",
        "patient_id": document.patient_id,
        "encounter_id": document.encounter_id,
        "extracted_entities": entities,
        "phi_redaction_preview": [finding["type"] for finding in findings],
        "pipeline_event_id": event["event_id"],
        "data_quality_flags": transformed["quality_flags"],
        "audit_id": audit_id,
    }


@router.post("/fhir/ingest")
def ingest_fhir(resource: FHIRResourceInput):
    service = FHIRIngestionService()
    payload = {**resource.payload, "resourceType": resource.resource_type, "id": resource.resource_id}
    validation = service.validate_resource(payload)
    if not validation["valid"]:
        raise HTTPException(status_code=400, detail=validation)
    normalized = service.normalize(payload)
    event = event_bus.publish("clinical.fhir.ingested", {"patient_id": resource.patient_id, **normalized})
    transformed = transformer.transform_patient_context_event(event)
    repo.save_patient_context(resource.patient_id, {"fhir": normalized})
    return {"status": "ingested", "validation": validation, "normalized": normalized, "pipeline_event_id": event["event_id"], "data_quality_flags": transformed["quality_flags"]}


@router.post("/hl7v2/ingest")
def ingest_hl7(message: HL7v2MessageInput):
    normalized = HL7v2IngestionService().normalize_message(message.raw_message)
    event = event_bus.publish("clinical.hl7v2.ingested", {"facility_id": message.facility_id, **normalized})
    transformed = transformer.transform_patient_context_event(event)
    return {
        "status": "ingested",
        "message_type": message.message_type,
        "facility_id": message.facility_id,
        "normalized_preview": normalized,
        "pipeline_event_id": event["event_id"],
        "data_quality_flags": transformed["quality_flags"],
    }


@router.post("/query", response_model=ClinicalSummaryResponse)
def clinical_query(request: ClinicalQueryRequest):
    graph = build_clinical_decision_graph()
    state = graph.invoke(request.model_dump())
    flags = sorted(set(guardrails.validate_query(request.question) + state.get("governance_flags", [])))
    return ClinicalSummaryResponse(
        patient_id=request.patient_id,
        encounter_id=request.encounter_id,
        answer=state.get("final_answer", ""),
        retrieved_context=state.get("retrieved_context", []),
        citations=state.get("validation_result", {}).get("citations", []),
        risk_scores=state.get("risk_scores", {}),
        governance_flags=flags,
        requires_human_review=state.get("human_review_required", True),
        audit_id=state.get("audit_id", ""),
    )


@router.get("/patient/{patient_id}/risk", response_model=RiskScoreResponse)
def patient_risk(patient_id: str):
    result = RiskScoringService(repo).calculate_patient_risk(patient_id)
    return RiskScoreResponse(
        patient_id=patient_id,
        readmission_risk=float(result["readmission_risk"]),
        risk_level=result["risk_level"],
        top_factors=result["top_factors"],
        model_version=result["model_version"],
        disclaimer=DECISION_SUPPORT_RISK_DISCLAIMER,
    )


@router.post("/evaluation/rag")
def evaluate_rag(request: RAGEvaluationRequest):
    return RAGEvaluator().evaluate(
        answer=request.answer,
        retrieved_context=request.retrieved_context,
        citations=request.citations,
    )


@router.get("/dashboard/export", response_model=DashboardExportResponse)
def export_dashboard():
    result = DashboardExporter().export(repo.list_dashboard_records())
    return DashboardExportResponse(
        json_path=result["json"],
        csv_path=result["csv"],
        summary=result["summary"],
    )


@router.get("/health")
def clinical_health():
    snapshot = metrics.snapshot()
    return {
        "api": "ok",
        "rag": "ok",
        "ml": "ok",
        "governance": "ok",
        "metrics": snapshot,
    }
