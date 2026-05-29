import os
from dataclasses import dataclass
from dotenv import load_dotenv

load_dotenv()

def _bool(name: str, default: bool = True) -> bool:
    return os.getenv(name, str(default)).strip().lower() in {"1", "true", "yes", "on"}

@dataclass(frozen=True)
class HealthcareSettings:
    app_env: str = os.getenv("APP_ENV", "local")
    curated_store_mode: str = os.getenv("CURATED_STORE_MODE", "local")
    local_curated_path: str = os.getenv("LOCAL_CURATED_PATH", "data/curated_store.json")
    vector_store_provider: str = os.getenv("VECTOR_STORE_PROVIDER", "qdrant")
    qdrant_url: str = os.getenv("QDRANT_URL", "")
    qdrant_api_key: str = os.getenv("QDRANT_API_KEY", "")
    llm_provider: str = os.getenv("LLM_PROVIDER", "azure_openai")
    azure_openai_endpoint: str = os.getenv("AZURE_OPENAI_ENDPOINT", os.getenv("azure_endpoint", ""))
    azure_openai_api_key: str = os.getenv("AZURE_OPENAI_API_KEY", os.getenv("openai_api_key", ""))
    azure_openai_api_version: str = os.getenv("AZURE_OPENAI_API_VERSION", os.getenv("openai_api_version", ""))
    azure_openai_deployment_name: str = os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME", os.getenv("deployment_name", ""))
    google_cloud_project: str = os.getenv("GOOGLE_CLOUD_PROJECT", "")
    bigquery_project_id: str = os.getenv("BIGQUERY_PROJECT_ID", os.getenv("GOOGLE_CLOUD_PROJECT", ""))
    bigquery_dataset: str = os.getenv("BIGQUERY_DATASET", "")
    cloud_healthcare_dataset: str = os.getenv("CLOUD_HEALTHCARE_DATASET", "")
    fhir_store: str = os.getenv("FHIR_STORE", "")
    hl7v2_store: str = os.getenv("HL7V2_STORE", "")
    enable_phi_redaction: bool = _bool("ENABLE_PHI_REDACTION", True)
    enable_rbac: bool = _bool("ENABLE_RBAC", True)
    enable_audit_logging: bool = _bool("ENABLE_AUDIT_LOGGING", True)
    enable_human_review: bool = _bool("ENABLE_HUMAN_REVIEW", True)
    enable_rag_eval: bool = _bool("ENABLE_RAG_EVAL", True)
    readmission_model_path: str = os.getenv("READMISSION_MODEL_PATH", "")
    audit_log_path: str = os.getenv("AUDIT_LOG_PATH", "logs/audit_log.jsonl")

settings = HealthcareSettings()
