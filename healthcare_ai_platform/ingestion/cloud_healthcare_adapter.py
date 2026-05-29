from typing import Any, Dict

from healthcare_ai_platform.ingestion.fhir_ingestion import FHIRIngestionService
from healthcare_ai_platform.ingestion.hl7v2_ingestion import HL7v2IngestionService


class CloudHealthcareAdapter:
    """Local-safe facade shaped like a cloud healthcare ingestion boundary."""

    def __init__(self):
        self.fhir = FHIRIngestionService()
        self.hl7v2 = HL7v2IngestionService()

    def ingest_fhir_resource(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        validation = self.fhir.validate_resource(payload)
        return {
            "source": "cloud_healthcare_style_fhir",
            "validation": validation,
            "normalized": self.fhir.normalize(payload) if validation["valid"] else None,
        }

    def ingest_hl7v2_message(self, raw_message: str) -> Dict[str, Any]:
        return {
            "source": "cloud_healthcare_style_hl7v2",
            "normalized": self.hl7v2.normalize_message(raw_message),
        }
