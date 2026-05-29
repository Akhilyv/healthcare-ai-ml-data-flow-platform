import csv, json
from collections import Counter
from pathlib import Path
from typing import Any, Dict, List
class DashboardExporter:
    def build_summary(self, records: List[Dict[str, Any]]) -> Dict[str, Any]:
        n=max(len(records),1)
        return {"requests_per_facility":dict(Counter(r.get("facility_id","unknown") for r in records)),"average_retrieval_count":sum(r.get("retrieval_count",0) for r in records)/n,"percentage_requiring_human_review":sum(1 for r in records if r.get("requires_human_review"))/n,"guardrail_failure_rate":sum(1 for r in records if r.get("guardrail_flags"))/n,"risk_distribution":dict(Counter(r.get("risk_level","unknown") for r in records)),"document_ingestion_counts":dict(Counter(r.get("document_type","unknown") for r in records)),"unsupported_claim_rate":sum(1 for r in records if "unsupported" in " ".join(r.get("guardrail_flags",[])))/n}

    def export(self, records: List[Dict[str, Any]], output_dir: str = "dashboard_outputs") -> Dict[str, Any]:
        path=Path(output_dir); path.mkdir(parents=True,exist_ok=True)
        summary=self.build_summary(records)
        jp=path/"clinical_dashboard_summary.json"; jp.write_text(json.dumps(summary,indent=2),encoding="utf-8"); cp=path/"clinical_dashboard_summary.csv"
        with cp.open("w",newline="",encoding="utf-8") as f:
            w=csv.writer(f); w.writerow(["metric","value"]); [w.writerow([k,json.dumps(v)]) for k,v in summary.items()]
        return {"json":str(jp),"csv":str(cp),"summary":summary}
