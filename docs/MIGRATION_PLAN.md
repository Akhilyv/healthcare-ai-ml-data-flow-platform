# Migration Plan

The original FastAPI app, UI, LangGraph medical assistant, Qdrant/RAG flow, Docling parser, guardrails, Dockerfile, and CI foundations are retained.

The upgrade adds healthcare_ai_platform as a modular package with local-safe abstractions for EHR, FHIR, HL7v2, document, and claims ingestion; Cloud Healthcare API-style adapters; a Pub/Sub-style local event bus; Dataflow-style transformations; curated data storage; clinical NLP; patient-context RAG; readmission support; governance; audit logging; human review; observability; evaluation; and dashboard exports.

The main app now includes /v2/clinical routes while preserving existing routes. Legacy Azure/LangChain paths are lazy-loaded so local health checks and clinical API tests can run without cloud credentials.

Production next steps include replacing local JSON with BigQuery, adding real Cloud Healthcare API connectors, enabling managed Pub/Sub/Dataflow, training and validating ML models, adding identity-aware RBAC, and completing HIPAA compliance controls.
