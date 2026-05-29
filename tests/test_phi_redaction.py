from healthcare_ai_platform.governance.phi_redaction import PHIRedactor

def test_phi_redaction_catches_email_phone_mrn():
    r=PHIRedactor(); text="MRN: ABC12345 call 555-123-4567 or alex@example.com"
    types={f["type"] for f in r.detect_phi(text)}
    assert {"mrn","phone","email"}.issubset(types)
    redacted=r.redact_text(text)
    assert "alex@example.com" not in redacted and "555-123-4567" not in redacted
