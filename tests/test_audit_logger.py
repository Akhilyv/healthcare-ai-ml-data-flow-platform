import json
from healthcare_ai_platform.governance.audit_logger import AuditLogger

def test_audit_logger_writes_jsonl_record(tmp_path):
    path=tmp_path/"audit.jsonl"; logger=AuditLogger(str(path)); audit_id=logger.start(user_id="u1",role="physician",patient_id="SYN",facility_id="F",route="test")
    lines=path.read_text().splitlines(); record=json.loads(lines[-1])
    assert record["audit_id"] == audit_id
    assert record["event"] == "start"
