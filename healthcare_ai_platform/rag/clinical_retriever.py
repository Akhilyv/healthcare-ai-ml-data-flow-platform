from typing import Any, Dict, List
from healthcare_ai_platform.curated.bigquery_repository import BigQueryRepository
class ClinicalRetriever:
    def __init__(self, repo: BigQueryRepository | None = None): self.repo=repo or BigQueryRepository()
    def _chunks_from_docs(self, docs: List[Dict[str, Any]], question: str) -> List[Dict[str, Any]]:
        terms={t.lower() for t in (question or "").split() if len(t)>3}; chunks=[]
        for i,d in enumerate(docs):
            content=d.get("redacted_text") or d.get("text") or ""; score=sum(1 for t in terms if t in content.lower())/max(len(terms),1)
            chunks.append({"id":f"doc-{i+1}","content":content[:1000],"score":score,"patient_id":d.get("patient_id"),"encounter_id":d.get("encounter_id"),"facility_id":d.get("facility_id"),"document_type":d.get("document_type"),"source":d.get("metadata",{}).get("source_system","curated_document")})
        return sorted(chunks,key=lambda c:c["score"], reverse=True)[:5]
    def retrieve_patient_context(self, patient_id: str, question: str, facility_id: str) -> List[Dict[str, Any]]: return self._chunks_from_docs([d for d in self.repo.get_patient_context(patient_id).get("documents",[]) if d.get("facility_id") in {facility_id,None,""}], question)
    def retrieve_policy_context(self, question: str, facility_id: str) -> List[Dict[str, Any]]: return [{"id":"policy-1","content":"Use retrieved patient facts only. Escalate urgent symptoms and keep clinicians in control.","score":0.5,"facility_id":facility_id,"document_type":"clinical_policy","source":"synthetic_policy"}]
    def retrieve_note_context(self, patient_id: str, encounter_id: str | None, question: str) -> List[Dict[str, Any]]:
        docs=self.repo.get_patient_context(patient_id).get("documents",[])
        if encounter_id: docs=[d for d in docs if d.get("encounter_id")==encounter_id]
        return self._chunks_from_docs(docs, question)
    def retrieve_similar_cases(self, question: str, filters: Dict[str, Any]) -> List[Dict[str, Any]]: return []
    def rerank_context(self, query: str, chunks: List[Dict[str, Any]]) -> List[Dict[str, Any]]: return sorted(chunks,key=lambda c:c.get("score",0), reverse=True)
