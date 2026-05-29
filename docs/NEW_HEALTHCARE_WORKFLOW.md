# New Healthcare Workflow

This project now models a production-style healthcare AI/ML data flow from clinical source systems to provider-facing decision support.

## 1. Data Sources / Inputs
- EHR and MEDITECH-style encounter, lab, diagnosis, medication, and note data.
- FHIR resources including Patient, Encounter, Observation, Condition, DiagnosticReport, and MedicationRequest.
- HL7v2 ADT, ORM, and ORU-style messages.
- Clinical notes, discharge summaries, scanned lab reports, and insurance forms.
- Claims and operational data.

## 2. Integration & Ingestion
The ingestion package provides Cloud Healthcare API-style abstractions, local mock connectors, Pub/Sub-style event boundaries, and Dataflow-style normalization hooks. Local mode requires no cloud credentials.

Implementation modules:

- `ingestion/cloud_healthcare_adapter.py`: facade for FHIR and HL7v2 ingestion shaped like a cloud healthcare API boundary.
- `ingestion/event_bus.py`: local in-memory Pub/Sub-style event bus for pipeline events.
- `ingestion/dataflow_transformer.py`: local Dataflow-style transformation and quality-flag stage.

## 3. Curated Data Layer
The BigQueryRepository abstraction writes to local JSON by default and can later map to curated datasets such as patient_encounters, lab_results, diagnosis_history, clinical_note_metadata, and readmission_features.

## 4. AI Processing Layer
Clinical NLP extracts sections, conditions, medications, labs, follow-up instructions, social risk, adherence risk, and risk signals. RAG retrieves patient and policy context with citations. Predictive ML uses a transparent deterministic baseline for readmission support and can optionally load a sklearn/joblib artifact when `READMISSION_MODEL_PATH` is configured.

## 5. Governance, Security, and Monitoring
The platform includes HIPAA/PHI design notes, PHI redaction, RBAC, audit logs, human review, clinical guardrails, RAG evaluation stubs, and OpenTelemetry/Prometheus-compatible naming hooks.

## 6. Outputs / Business Outcomes
Outputs include provider-facing clinical summaries, retrieved patient context, patient-risk/readmission support, analytics-ready dashboard exports, reduced manual review burden, and clinician-controlled final decisions.
