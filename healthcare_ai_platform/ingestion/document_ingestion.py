from pathlib import Path
from typing import Any, Dict
class DocumentIngestionService:
    def parse_document(self, path: str | None = None, text: str | None = None, metadata: Dict[str, Any] | None = None) -> Dict[str, Any]:
        metadata=metadata or {}
        if text is None and path:
            suffix=Path(path).suffix.lower()
            if suffix in {".txt",".md",".hl7"}: text=Path(path).read_text(encoding="utf-8")
            else:
                try:
                    from agents.rag_agent.doc_parser import MedicalDocParser
                    parsed,_=MedicalDocParser().parse_document(path,"data/parsed_docs"); text=parsed.export_to_markdown() if hasattr(parsed,"export_to_markdown") else str(parsed)
                except Exception as exc: text=f"Document parsing unavailable locally: {exc}"
        return {"text":text or "", "metadata":metadata, "tables":metadata.get("tables",[]), "parser":"docling_wrapper_or_text_fallback"}
