import os
import json
import pandas as pd
from config import EMBEDDING_MODEL

class Offer:
    def __init__(self, raw_data: dict):
        self.raw = raw_data
        self.vector = self._compute_embedding()

    def _compute_embedding(self):
        try:
            # Convierte listas a texto, ignora valores no representables
            parts = []
            for v in self.raw.values():
                if isinstance(v, list):
                    parts.append(", ".join(map(str, v)))
                elif isinstance(v, (str, int, float)):
                    parts.append(str(v))
            relevant_text = " ".join(parts)
            return EMBEDDING_MODEL.encode(relevant_text)
        except Exception:
            return None  # fallback en caso de error

def load_offers_from_directory(json_dir):
    offers = []
    for file in os.listdir(json_dir):
        path = os.path.join(json_dir, file)
        if file.endswith(".json"):
            try:
                with open(path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    for item in data:
                        if isinstance(item, dict):
                            offers.append(Offer(item))
            except Exception as e:
                print(f"[JSON error] {file}: {e}")

        elif file.endswith(".csv"):
            try:
                df = pd.read_csv(path)
                for _, row in df.iterrows():
                    offers.append(Offer(row.to_dict()))
            except Exception as e:
                print(f"[CSV error] {file}: {e}")

    return offers
