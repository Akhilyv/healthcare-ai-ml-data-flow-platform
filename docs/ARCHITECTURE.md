# Architecture

## Folder Structure
The healthcare_ai_platform package is organized by API, core settings, ingestion, curated data, NLP, RAG, ML, workflows, governance, observability, evaluation, and dashboard exports.

## Sequence Flow
EHR / FHIR / HL7v2 / Clinical Notes / Scanned Docs / Claims -> Cloud Healthcare API-style ingestion -> Pub/Sub-style event bus -> Dataflow-style transformation -> BigQuery-style curated layer -> Clinical NLP + RAG + Predictive ML -> Governance / RBAC / PHI redaction / Audit logs -> Provider-facing summary, retrieved context, patient-risk support, analytics.

## API Flow
New routes live under /v2/clinical and do not replace existing /chat, /upload, /validate, /transcribe, or /generate-speech routes. Ingestion routes publish local pipeline events and pass through a Dataflow-style quality transformation before records are stored in the curated layer. Platform operations routes expose RAG evaluation and dashboard exports.

## LangGraph Flow
validate_request -> rbac -> patient_context -> clinical_nlp -> retrieval -> risk_model -> generation -> grounding_validation -> guardrail -> human_review -> final_response.

When LangGraph is installed, `build_clinical_decision_graph()` compiles this flow as a `StateGraph`. When LangGraph is not installed, the same public `graph.invoke(request)` contract uses a deterministic local runner so tests and local demos do not require external graph dependencies.

Conditional behavior:
- RBAC denial routes directly to `final_response`.
- Insufficient retrieved patient context forces the answer to say evidence is insufficient and requires human review.
- High-risk scores, low grounding, unsupported claims, or missing citations force human review.

## Data Contracts
Strict Pydantic schemas in healthcare_ai_platform/api/schemas.py define clinical documents, FHIR resources, HL7v2 messages, query requests, summaries, and risk responses.
