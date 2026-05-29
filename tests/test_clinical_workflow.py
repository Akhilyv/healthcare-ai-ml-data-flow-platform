from healthcare_ai_platform.workflows.clinical_decision_graph import build_clinical_decision_graph
from healthcare_ai_platform.observability.metrics import CLINICAL_REQUESTS_TOTAL, metrics
from healthcare_ai_platform.observability.tracing import tracer

def test_human_review_required_for_low_grounding_response():
    before = metrics.snapshot()["counters"].get(CLINICAL_REQUESTS_TOTAL, 0)
    state=build_clinical_decision_graph().invoke({"user_id":"u1","role":"physician","patient_id":"NO-DOC","encounter_id":"E1","facility_id":"F1","question":"Summarize discharge risk","include_risk_score":True,"require_human_review":False})
    assert state["human_review_required"]
    assert "Evidence is insufficient" in state["final_answer"]
    assert metrics.snapshot()["counters"][CLINICAL_REQUESTS_TOTAL] >= before + 1
    assert any(event.get("workflow.node.name") == "validate_request_node" for event in tracer.events)
