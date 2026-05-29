from typing import Dict

class NoteSectionizer:
    HEADINGS = ["history", "assessment", "plan", "medications", "labs", "discharge instructions", "follow up", "follow-up"]

    def sectionize(self, text: str) -> Dict[str, str]:
        sections = {"general": []}
        current = "general"
        for line in (text or "").splitlines():
            clean = line.strip().strip(":").lower()
            if clean in self.HEADINGS:
                current = "follow_up" if clean in {"follow up", "follow-up"} else clean.replace(" ", "_")
                sections.setdefault(current, [])
            else:
                sections.setdefault(current, []).append(line)
        return {k: "\n".join(v).strip() for k, v in sections.items() if "\n".join(v).strip()}
