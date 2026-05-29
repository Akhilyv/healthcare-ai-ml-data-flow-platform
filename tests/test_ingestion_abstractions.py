from healthcare_ai_platform.ingestion.cloud_healthcare_adapter import CloudHealthcareAdapter
from healthcare_ai_platform.ingestion.dataflow_transformer import ClinicalDataflowTransformer
from healthcare_ai_platform.ingestion.event_bus import LocalClinicalEventBus


def test_cloud_healthcare_event_bus_and_dataflow_abstractions_are_local_safe():
    adapter = CloudHealthcareAdapter()
    result = adapter.ingest_fhir_resource({"resourceType": "Patient", "id": "SYN-123"})
    assert result["validation"]["valid"]

    bus = LocalClinicalEventBus()
    event = bus.publish("clinical.patient_context", {"patient_id": "SYN-123", "facility_id": "FAC-1"})
    transformed = ClinicalDataflowTransformer().transform_patient_context_event(event)
    assert transformed["quality_flags"] == []
    assert transformed["curated_record"]["patient_id"] == "SYN-123"
