from typing import Dict, List

class HL7v2IngestionService:
    def parse_segments(self, raw_message: str) -> Dict[str, List[List[str]]]:
        segments = {}
        for line in (raw_message or "").replace("\n", "\r").split("\r"):
            if not line.strip():
                continue
            fields = line.split("|")
            segments.setdefault(fields[0], []).append(fields)
        return segments

    def extract_message_header(self, raw_message: str) -> Dict[str, str]:
        msh = self.parse_segments(raw_message).get("MSH", [[]])[0]
        return {"sending_app": msh[2] if len(msh) > 2 else "", "message_type": msh[8] if len(msh) > 8 else "", "control_id": msh[9] if len(msh) > 9 else ""}

    def extract_patient_identifier(self, raw_message: str) -> str:
        pid = self.parse_segments(raw_message).get("PID", [[]])[0]
        return pid[3] if len(pid) > 3 else ""

    def extract_event_type(self, raw_message: str) -> str:
        msg = self.extract_message_header(raw_message).get("message_type", "")
        return msg.split("^")[1] if "^" in msg else msg

    def normalize_message(self, raw_message: str) -> Dict[str, str]:
        header = self.extract_message_header(raw_message)
        return {**header, "patient_identifier": self.extract_patient_identifier(raw_message), "event_type": self.extract_event_type(raw_message)}
