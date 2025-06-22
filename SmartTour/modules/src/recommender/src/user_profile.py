from config import EMBEDDING_MODEL

class UserProfile:
    def __init__(self, data: dict):
        self.raw = data
        self.vector = self._compute_embedding()

    def _compute_embedding(self):
        combined = " ".join([f"{k}: {v}" for k, v in self.raw.items() if isinstance(v, str)])
        return EMBEDDING_MODEL.encode(combined)
