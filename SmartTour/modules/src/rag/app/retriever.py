# app/retriever.py
from qdrant_client import QdrantClient
from qdrant_client.http.models import Distance, VectorParams, PointStruct
from sentence_transformers import SentenceTransformer
import json
import uuid

class Retriever:
    def __init__(self, config):
        self.config = config
        self.model = SentenceTransformer(config["retriever"]["model"])
        self.qdrant = QdrantClient(host="localhost", port=6333)
        self.collection_name = config["retriever"]["collection"]
        self._init_collection()
        self._load_documents(config["retriever"]["knowledge_base"])

    def _init_collection(self):
        if not self.qdrant.collection_exists(self.collection_name):
            self.qdrant.create_collection(
                collection_name=self.collection_name,
                vectors_config=VectorParams(
                    size=768, distance=Distance.COSINE
                )
            )

    def _load_documents(self, path):
        with open(path, "r", encoding="utf-8") as f:
            docs = json.load(f)

        existing = self.qdrant.count(self.collection_name).count
        if existing >= len(docs):
            return  # Skip if already loaded

        points = []
        for doc in docs:
            vector = self.model.encode(doc["content"]).tolist()
            points.append(PointStruct(
                id=str(uuid.uuid4()),
                vector=vector,
                payload={"text": doc["content"]}
            ))

        self.qdrant.upsert(
            collection_name=self.collection_name,
            points=points
        )

    def retrieve(self, query, k=3):
        vector = self.model.encode(query).tolist()
        hits = self.qdrant.search(
            collection_name=self.collection_name,
            query_vector=vector,
            limit=k
        )
        return [hit.payload["text"] for hit in hits]
