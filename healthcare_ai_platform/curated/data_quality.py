from datetime import datetime
from typing import Any, Dict, Iterable, List
class DataQualityValidator:
    def required_fields(self, payload: Dict[str, Any], fields: Iterable[str]) -> List[str]: return [f"missing_{f}" for f in fields if not payload.get(f)]
    def null_checks(self, payload: Dict[str, Any]) -> List[str]: return [f"null_{k}" for k,v in payload.items() if v is None]
    def patient_id_consistency(self, *patient_ids: str) -> bool: return len(set([p for p in patient_ids if p])) <= 1
    def encounter_id_consistency(self, *encounter_ids: str) -> bool: return len(set([e for e in encounter_ids if e])) <= 1
    def duplicate_detection(self, records: List[Dict[str, Any]], key: str) -> List[str]:
        seen=set(); dup=[]
        for r in records:
            v=r.get(key)
            if v in seen: dup.append(str(v))
            seen.add(v)
        return dup
    def validate_date(self, value: str) -> bool:
        for fmt in ("%Y-%m-%d","%Y-%m-%dT%H:%M:%S","%m/%d/%Y"):
            try: datetime.strptime(value, fmt); return True
            except ValueError: pass
        return False
