# app/retriever.py
from sentence_transformers import SentenceTransformer
import json
import uuid

class Retriever:
    def __init__(self, config):
        self.config = config
        self.model = SentenceTransformer(config["retriever"]["model"])
        try:
            from qdrant_client import QdrantClient
            self.qdrant = QdrantClient(host="localhost", port=6333)
            self.collection_name = config["retriever"]["collection"]
            self._init_collection()
            self._load_documents(config["retriever"]["knowledge_base"])
        except Exception as e:
            import streamlit as st
            st.error(
                "❌ Could not connect to Qdrant server at localhost:6333. "
                "Please ensure Qdrant is running.\n\n"
                f"Error: {e}"
            )
            self.qdrant = None
            self.collection_name = None

    def _init_collection(self):
        if self.qdrant is None:
            return
        try:
            if not self.qdrant.collection_exists(self.collection_name):
                from qdrant_client.http.models import Distance, VectorParams
                self.qdrant.create_collection(
                    collection_name=self.collection_name,
                    vectors_config=VectorParams(
                        size=768, distance=Distance.COSINE
                    )
                )
        except Exception as e:
            import streamlit as st
            st.error(f"❌ Error initializing Qdrant collection: {e}")

    def _load_documents(self, path):
        if self.qdrant is None:
            return
        import uuid
        import json
        try:
            with open(path, "r", encoding="utf-8") as f:
                docs = json.load(f)

            existing = self.qdrant.count(self.collection_name).count
            if existing >= len(docs):
                return  # Skip if already loaded

            from qdrant_client.http.models import PointStruct
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
        except Exception as e:
            import streamlit as st
            st.error(f"❌ Error loading documents into Qdrant: {e}")

    def retrieve(self, query, k=3):
        if self.qdrant is None:
            return []
        try:
            vector = self.model.encode(query).tolist()
            hits = self.qdrant.search(
                collection_name=self.collection_name,
                query_vector=vector,
                limit=k
            )
            return [hit.payload["text"] for hit in hits]
        except Exception as e:
            import streamlit as st
            st.error(f"❌ Error retrieving from Qdrant: {e}")
            return []
