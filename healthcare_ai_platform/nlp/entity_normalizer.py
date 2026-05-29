class EntityNormalizer:
    TERM_MAP = {"chf": "heart failure", "ckd": "chronic kidney disease", "htn": "hypertension", "dm": "diabetes mellitus", "a1c": "hemoglobin A1C"}
    def normalize(self, term: str) -> str: return self.TERM_MAP.get((term or "").lower(), term.lower() if term else term)
    def normalize_many(self, terms): return [self.normalize(term) for term in terms]
