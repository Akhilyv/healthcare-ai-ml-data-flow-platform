from typing import Any, Dict
from healthcare_ai_platform.curated.bigquery_repository import BigQueryRepository
from healthcare_ai_platform.governance.audit_logger import AuditLogger
from healthcare_ai_platform.governance.guardrails import ClinicalGuardrails
from healthcare_ai_platform.governance.human_review import HumanReviewService
from healthcare_ai_platform.governance.rbac import RBACPolicy
from healthcare_ai_platform.ml.risk_scoring import RiskScoringService
from healthcare_ai_platform.nlp.clinical_nlp import ClinicalNLPService
from healthcare_ai_platform.observability.metrics import CLINICAL_REQUESTS_TOTAL, metrics
from healthcare_ai_platform.observability.tracing import tracer
from healthcare_ai_platform.rag.clinical_retriever import ClinicalRetriever
from healthcare_ai_platform.rag.source_citation import SourceCitationService

repo = BigQueryRepository()
audit = AuditLogger()
rbac = RBACPolicy()
nlp = ClinicalNLPService()
retriever = ClinicalRetriever(repo)
risk_service = RiskScoringService(repo)
citation_service = SourceCitationService()
guardrails = ClinicalGuardrails()
human_review = HumanReviewService()

def validate_request_node(state: Dict[str, Any]) -> Dict[str, Any]:
    req = state["request"]
    metrics.increment(CLINICAL_REQUESTS_TOTAL)
    flags = [f"missing_{f}" for f in ["user_id", "role", "patient_id", "facility_id", "question"] if not req.get(f)]
    audit_id = audit.start(user_id=req.get("user_id"), role=req.get("role"), patient_id=req.get("patient_id"), facility_id=req.get("facility_id"), route="/v2/clinical/query")
    return {**state, "audit_id": audit_id, "governance_flags": flags}

def rbac_node(state):
    req = state["request"]
    decision = rbac.authorize(req.get("role"), "patient_context", req.get("patient_id"))
    flags = state.get("governance_flags", [])
    if not decision.allowed:
        flags.append("access_denied")
    return {**state, "user_context": {"rbac": decision.__dict__}, "access_denied": not decision.allowed, "governance_flags": flags}

def patient_context_node(state):
    if state.get("access_denied"):
        return state
    req = state["request"]
    context = repo.get_encounter_context(req["patient_id"], req["encounter_id"]) if req.get("encounter_id") else repo.get_patient_context(req["patient_id"])
    if state.get("user_context", {}).get("rbac", {}).get("deidentified_only"):
        context = _deidentify_context(context)
    audit.log(audit_id=state["audit_id"], event="patient_context_loaded", document_count=len(context.get("documents", [])))
    tracer.log_event("clinical.patient_context.loaded", {"clinical.patient_context.loaded": True, "document_count": len(context.get("documents", []))})
    return {**state, "patient_context": context}


def _deidentify_context(context: Dict[str, Any]) -> Dict[str, Any]:
    redacted = {k: v for k, v in context.items() if k not in {"patient_id", "latest_encounter", "fhir"}}
    redacted["documents"] = []
    for document in context.get("documents", []):
        redacted["documents"].append({
            "encounter_id": document.get("encounter_id"),
            "facility_id": document.get("facility_id"),
            "document_type": document.get("document_type"),
            "redacted_text": document.get("redacted_text", ""),
            "metadata": {"deidentified": True, "source_system": document.get("metadata", {}).get("source_system")},
        })
    redacted["deidentified"] = True
    return redacted

def clinical_nlp_node(state):
    texts = "\n".join(d.get("redacted_text") or d.get("text", "") for d in state.get("patient_context", {}).get("documents", []))
    return {**state, "nlp_signals": nlp.extract_entities(texts)}

def retrieval_node(state):
    req = state["request"]
    chunks = retriever.retrieve_note_context(req["patient_id"], req.get("encounter_id"), req["question"]) + retriever.retrieve_policy_context(req["question"], req["facility_id"])
    chunks = retriever.rerank_context(req["question"], chunks)
    if state.get("user_context", {}).get("rbac", {}).get("deidentified_only"):
        chunks = [_deidentify_chunk(chunk) for chunk in chunks]
    audit.log(audit_id=state["audit_id"], event="retrieval", retrieval_count=len(chunks))
    return {**state, "retrieved_context": chunks}


def _deidentify_chunk(chunk: Dict[str, Any]) -> Dict[str, Any]:
    safe = chunk.copy()
    safe.pop("patient_id", None)
    safe["content"] = safe.get("content", "")
    safe["deidentified"] = True
    return safe

def risk_model_node(state):
    req = state["request"]
    risk = risk_service.calculate_patient_risk(req["patient_id"]) if req.get("include_risk_score", True) else {}
    audit.log(audit_id=state["audit_id"], event="risk_score", risk_score=risk.get("readmission_risk"))
    return {**state, "risk_scores": risk}

def generation_node(state):
    tracer.log_event(
        "gen_ai.request",
        {
            "gen_ai.request.model": "deterministic_local_summary",
            "gen_ai.tool.name": "clinical_summary_generator",
        },
    )
    patient_chunks = [c for c in state.get("retrieved_context", []) if c.get("document_type") != "clinical_policy"]
    if not patient_chunks:
        answer = "Evidence is insufficient in the retrieved patient context to answer the clinical question."
    else:
        conditions = ", ".join(state.get("nlp_signals", {}).get("conditions", [])) or "no extracted conditions"
        risk = state.get("risk_scores", {})
        answer = f"Based on retrieved context, key extracted signals include {conditions}. Readmission support risk is {risk.get('risk_level', 'not calculated')} ({risk.get('readmission_risk', 'n/a')}). Use cited context to verify details before action."
    tracer.log_event(
        "gen_ai.usage",
        {
            "gen_ai.usage.input_tokens": len(str(state.get("retrieved_context", [])).split()),
            "gen_ai.usage.output_tokens": len(answer.split()),
        },
    )
    return {**state, "draft_answer": guardrails.add_disclaimer(answer)}

def grounding_validation_node(state):
    cites = citation_service.build_citations(state.get("retrieved_context", []))
    validation = citation_service.validate_answer_grounding(state.get("draft_answer", ""), cites)
    unsupported = citation_service.detect_unsupported_claims(state.get("draft_answer", ""), state.get("retrieved_context", []))
    flags = state.get("governance_flags", []) + validation.get("flags", []) + unsupported
    return {**state, "validation_result": {**validation, "citations": cites}, "governance_flags": sorted(set(flags))}

def guardrail_node(state):
    flags = state.get("governance_flags", []) + guardrails.check_output(state.get("draft_answer", ""), state.get("validation_result", {}).get("citations", [])) + guardrails.validate_query(state["request"].get("question", ""))
    return {**state, "governance_flags": sorted(set(flags))}

def human_review_node(state):
    risk = state.get("risk_scores", {})
    insufficient_evidence = "evidence is insufficient" in state.get("draft_answer", "").lower()
    requires = (
        state["request"].get("require_human_review", True)
        or risk.get("risk_level") == "high"
        or insufficient_evidence
        or bool(set(state.get("governance_flags", [])) & {"ungrounded_answer", "missing_citation", "unsupported_diagnosis_claim"})
    )
    review_package = human_review.create_review_package(state["request"], state.get("draft_answer", ""), state.get("retrieved_context", []), state.get("governance_flags", [])) if requires else None
    return {**state, "human_review_required": requires, "review_package": review_package}

def final_response_node(state):
    if state.get("access_denied"):
        state = {**state, "draft_answer": guardrails.add_disclaimer("Access denied for this role and patient-context request."), "retrieved_context": [], "risk_scores": {}, "validation_result": {"citations": []}, "human_review_required": True}
    audit.log(audit_id=state["audit_id"], event="final", guardrail_flags=state.get("governance_flags", []), human_review_required=state.get("human_review_required", True))
    return {**state, "final_answer": state.get("draft_answer", "")}
