from typing import Any, Dict, List
class VectorStoreAdapter:
    def __init__(self, provider: str = "qdrant"): self.provider=provider; self._memory=[]
    def upsert_documents(self, documents: List[Dict[str, Any]]) -> Dict[str, Any]: self._memory.extend(documents); return {"status":"ok","count":len(documents),"provider":self.provider}
    def similarity_search(self, query: str, k: int = 5) -> List[Dict[str, Any]]: return self._memory[:k]
    def hybrid_search(self, query: str, k: int = 5, filters: Dict[str, Any] | None = None) -> List[Dict[str, Any]]: return self.metadata_filter_search(filters or {}, k)
    def metadata_filter_search(self, filters: Dict[str, Any], k: int = 5) -> List[Dict[str, Any]]: return [d for d in self._memory if all(d.get(key)==value for key,value in filters.items())][:k]
    def delete_by_patient(self, patient_id: str) -> int:
        before=len(self._memory); self._memory=[d for d in self._memory if d.get("patient_id")!=patient_id]; return before-len(self._memory)
    def delete_by_facility(self, facility_id: str) -> int:
        before=len(self._memory); self._memory=[d for d in self._memory if d.get("facility_id")!=facility_id]; return before-len(self._memory)
