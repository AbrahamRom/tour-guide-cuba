from sentence_transformers import SentenceTransformer
import faiss
import numpy as np
import json
import os

class Retriever:
    def __init__(self, config, kb_path="modules/src/rag/data/knowledge_base.json"):
        self.model = SentenceTransformer(config["retriever"]["model"])
        self.k = config["retriever"]["top_k"]
        self.documents = self._load_documents(kb_path)
        self.index, self.doc_map = self._build_index()

    def _load_documents(self, path):
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)

    def _build_index(self):
        embeddings = []
        doc_map = {}
        for i, doc in enumerate(self.documents):
            emb = self.model.encode(doc["content"])
            embeddings.append(emb)
            doc_map[i] = doc["content"]
        index = faiss.IndexFlatL2(len(embeddings[0]))
        index.add(np.array(embeddings))
        return index, doc_map

    def retrieve(self, query):
        query_vec = self.model.encode(query)
        D, I = self.index.search(np.array([query_vec]), self.k)
        return [self.doc_map[i] for i in I[0]]
