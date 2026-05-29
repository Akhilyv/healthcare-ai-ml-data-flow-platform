# API Contracts

## POST /v2/clinical/documents/ingest
Request: ClinicalDocumentInput with patient_id, encounter_id, facility_id, document_type, text, and metadata.
Response: ingestion status, extracted_entities, phi_redaction_preview, pipeline_event_id, data_quality_flags, and audit_id.

## POST /v2/clinical/fhir/ingest
Request: FHIRResourceInput.
Response: validation, normalized preview, pipeline_event_id, and data_quality_flags.

## POST /v2/clinical/hl7v2/ingest
Request: HL7v2MessageInput.
Response: normalized message header, event type, patient identifier preview, pipeline_event_id, and data_quality_flags.

## POST /v2/clinical/query
Request: ClinicalQueryRequest.
Response: ClinicalSummaryResponse containing answer, retrieved_context, citations, risk_scores, governance_flags, requires_human_review, and audit_id.

## GET /v2/clinical/patient/{patient_id}/risk
Response: RiskScoreResponse. The score is decision support only and is not clinically validated.

Example response:

```json
{
  "patient_id": "SYN-001",
  "readmission_risk": 0.42,
  "risk_level": "medium",
  "top_factors": [
    {"factor": "has_follow_up_gap", "contribution": 0.15, "value": true}
  ],
  "model_version": "deterministic-baseline-0.1-not-clinically-validated",
  "disclaimer": "This readmission score is decision support only, is not clinically validated, and must not be used as a final diagnosis or treatment decision."
}
```

## GET /v2/clinical/health
Response: api, rag, ml, governance health states, and an in-memory metrics snapshot.

Example response:

```json
{
  "api": "ok",
  "rag": "ok",
  "ml": "ok",
  "governance": "ok",
  "metrics": {
    "counters": {"clinical_requests_total": 3},
    "gauges": {"rag_retrieval_latency_ms": 2.4}
  }
}
```

## POST /v2/clinical/evaluation/rag
Request:

```json
{
  "answer": "Evidence is insufficient.",
  "retrieved_context": [],
  "citations": []
}
```

Response: heuristic or optional-RAGAS RAG evaluation metrics including context_relevance, groundedness, answer_faithfulness, citation_coverage, unsupported_claim_count, and retrieval_count.

## GET /v2/clinical/dashboard/export
Response: analytics-ready JSON/CSV output paths plus summary metrics for requests per facility, retrieval count, human review rate, guardrail failure rate, risk distribution, document ingestion counts, and unsupported claim rate.
