from healthcare_ai_platform.rag.source_citation import SourceCitationService

def test_unsupported_claims_trigger_governance_flag():
    svc=SourceCitationService()
    assert "unsupported_diagnosis_claim" in svc.detect_unsupported_claims("Unsupported diagnosis: pneumonia", [])
