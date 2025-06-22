from config import EMBEDDING_MODEL

class UserProfile:
    def __init__(self, data: dict):
        self.raw = data
        self.vector = self._compute_embedding()

    def _flatten_and_describe(self, obj, prefix=""):
        """
        Recursively flattens and summarizes the user JSON for embedding.
        Supports nested fields, lists, optional fields, and unknown keys.
        """
        parts = []
        if isinstance(obj, dict):
            for k, v in obj.items():
                parts.extend(self._flatten_and_describe(v, prefix + k + ": "))
        elif isinstance(obj, list):
            parts.append(prefix + ", ".join(map(str, obj)))
        elif isinstance(obj, (str, int, float, bool)):
            parts.append(f"{prefix}{obj}")
        return parts

    def _compute_embedding(self):
        try:
            combined_description = ". ".join(self._flatten_and_describe(self.raw))
        except Exception as e:
            combined_description = str(self.raw)  # fallback
        return EMBEDDING_MODEL.encode(combined_description)
