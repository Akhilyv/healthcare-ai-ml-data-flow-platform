from typing import Any, Dict

from healthcare_ai_platform.curated.data_quality import DataQualityValidator


class ClinicalDataflowTransformer:
    """Dataflow-style normalization and validation stage for local pipelines."""

    def __init__(self):
        self.validator = DataQualityValidator()

    def transform_patient_context_event(self, event: Dict[str, Any]) -> Dict[str, Any]:
        payload = event.get("payload", {})
        quality_flags = self.validator.required_fields(payload, ["patient_id"])
        return {
            "event_id": event.get("event_id"),
            "topic": event.get("topic"),
            "quality_flags": quality_flags,
            "curated_record": {
                "patient_id": payload.get("patient_id"),
                "encounter_id": payload.get("encounter_id"),
                "facility_id": payload.get("facility_id"),
                "source_system": payload.get("source_system", "local_mock"),
                "payload": payload,
            },
        }
