# Governance And Evaluation

## RBAC Matrix
- physician: full patient clinical context.
- nurse: assigned patient summaries and care tasks.
- care_manager: risk factors and discharge/follow-up information with de-identified retrieved context.
- analyst: de-identified or aggregated data only.
- admin: audit/config access, not full PHI by default.

## PHI Redaction Strategy
The PHIRedactor detects MRN-like IDs, phone numbers, emails, SSNs, obvious addresses, optional dates, and metadata-provided patient names.

## Audit Logging Schema
JSONL audit records include audit_id, user_id, role, patient_id, facility_id, route, timestamp, executed events, retrieval count, risk score, guardrail flags, and human review requirement.

## Human Review Rules
Clinical answers require clinician review by default, and review is forced for high-risk outputs, low grounding, unsupported claims, or access/governance flags.

## RAG Eval Metrics
Heuristic local metrics include context_relevance, groundedness, answer_faithfulness, citation_coverage, unsupported_claim_count, and retrieval_count. RAGAS/TruLens can be added without changing route contracts.

## Clinical Safety Rules
The system must not replace clinicians, must avoid unsupported diagnosis or treatment recommendations, must cite retrieved context or say evidence is insufficient, and must include the decision-support disclaimer.

## Observability Hooks
The workflow records lightweight local metrics with Prometheus-compatible names:

- `clinical_requests_total`
- `rag_retrieval_latency_ms`
- `llm_latency_ms`
- `risk_model_latency_ms`
- `guardrail_failures_total`
- `human_review_required_total`
- `unsupported_claims_total`
- `phi_redaction_events_total`

Tracing events use OpenTelemetry-compatible attribute names where practical, including `workflow.node.name`, `gen_ai.request.model`, `gen_ai.usage.input_tokens`, `gen_ai.usage.output_tokens`, `gen_ai.tool.name`, and `clinical.patient_context.loaded`.
