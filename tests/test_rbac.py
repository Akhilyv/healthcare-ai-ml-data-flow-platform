from healthcare_ai_platform.governance.rbac import RBACPolicy

def test_rbac_blocks_analyst_from_full_phi_patient_context():
    decision=RBACPolicy().authorize("analyst","patient_context","SYN-001")
    assert not decision.allowed
    assert decision.deidentified_only
