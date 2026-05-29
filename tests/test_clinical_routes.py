from fastapi.testclient import TestClient
from app import app

client=TestClient(app)

def test_api_import_and_health():
    r=client.get("/v2/clinical/health")
    assert r.status_code == 200
    assert r.json()["api"] == "ok"

def test_document_ingestion_returns_entities():
    payload={"patient_id":"SYN-ROUTE","encounter_id":"ENC-1","facility_id":"FAC-1","document_type":"discharge_summary","text":"Assessment: CHF and CKD. Creatinine 1.9. Follow-up within 7 days. Transportation barrier.","metadata":{"source_system":"synthetic"}}
    r=client.post("/v2/clinical/documents/ingest", json=payload)
    assert r.status_code == 200
    body=r.json()
    assert "heart failure" in body["extracted_entities"]["conditions"]
    assert body["pipeline_event_id"]
    assert body["data_quality_flags"] == []
    assert body["audit_id"]

def test_clinical_query_returns_decision_support_disclaimer():
    client.post("/v2/clinical/documents/ingest", json={"patient_id":"SYN-Q","encounter_id":"ENC-Q","facility_id":"FAC-1","document_type":"note","text":"CHF with missed medications and creatinine 1.8.","metadata":{}})
    r=client.post("/v2/clinical/query", json={"user_id":"doc1","role":"physician","patient_id":"SYN-Q","encounter_id":"ENC-Q","facility_id":"FAC-1","question":"What is the readmission risk context?","include_risk_score":True,"require_human_review":True})
    assert r.status_code == 200
    body=r.json()
    assert "clinical decision support" in body["answer"].lower()
    assert body["requires_human_review"]

def test_patient_risk_endpoint():
    r=client.get("/v2/clinical/patient/SYN-Q/risk")
    assert r.status_code == 200
    assert 0 <= r.json()["readmission_risk"] <= 1
    assert "decision support" in r.json()["disclaimer"].lower()


def test_clinical_health_exposes_metrics_snapshot():
    r=client.get("/v2/clinical/health")
    assert r.status_code == 200
    assert "metrics" in r.json()


def test_rag_evaluation_endpoint_and_dashboard_export():
    eval_response=client.post("/v2/clinical/evaluation/rag", json={"answer":"Evidence is insufficient.", "retrieved_context":[], "citations":[]})
    assert eval_response.status_code == 200
    assert eval_response.json()["unsupported_claim_count"] == 0

    dashboard_response=client.get("/v2/clinical/dashboard/export")
    assert dashboard_response.status_code == 200
    assert "requests_per_facility" in dashboard_response.json()["summary"]


def test_care_manager_gets_deidentified_context():
    client.post("/v2/clinical/documents/ingest", json={"patient_id":"SYN-CM","encounter_id":"ENC-CM","facility_id":"FAC-1","document_type":"note","text":"CHF with follow-up within 7 days. Phone 555-111-2222.","metadata":{}})
    r=client.post("/v2/clinical/query", json={"user_id":"cm1","role":"care_manager","patient_id":"SYN-CM","encounter_id":"ENC-CM","facility_id":"FAC-1","question":"What follow-up risks exist?","include_risk_score":True,"require_human_review":True})
    assert r.status_code == 200
    body=r.json()
    assert body["retrieved_context"]
    assert all("patient_id" not in chunk for chunk in body["retrieved_context"])
    assert any(chunk.get("deidentified") for chunk in body["retrieved_context"])
