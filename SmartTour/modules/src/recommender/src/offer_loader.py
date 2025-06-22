import os
import json
from config import EMBEDDING_MODEL

class Offer:
    def __init__(self, raw_data: dict):
        self.raw = raw_data
        self.vector = self._compute_embedding()

    def _compute_embedding(self):
        relevant_text = " ".join([str(v) for v in self.raw.values() if isinstance(v, str) or isinstance(v, list)])
        return EMBEDDING_MODEL.encode(relevant_text)

def load_offers_from_directory(json_dir):
    offers = []
    for file in os.listdir(json_dir):
        if file.endswith(".json"):
            with open(os.path.join(json_dir, file), "r", encoding="utf-8") as f:
                data = json.load(f)
                for item in data:
                    offers.append(Offer(item))
    return offers
