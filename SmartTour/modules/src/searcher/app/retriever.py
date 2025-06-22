from sentence_transformers import SentenceTransformer, util
import os, json
import numpy as np
import pickle

class Retriever:
    def __init__(self, model_name='all-MiniLM-L6-v2', data_dir='modules/src/searcher/data/documents', embedding_cache='modules/src/searcher/embeddings/doc_embeddings.pkl'):
        self.model = SentenceTransformer(model_name)
        self.data_dir = data_dir
        self.embedding_cache = embedding_cache
        self.documents = []
        self.embeddings = None
        self.load_documents()

    def load_documents(self):
        if os.path.exists(self.embedding_cache):
            with open(self.embedding_cache, 'rb') as f:
                self.documents, self.embeddings = pickle.load(f)
        else:
            for filename in os.listdir(self.data_dir):
                if filename.endswith('.json'):
                    with open(os.path.join(self.data_dir, filename), 'r', encoding='utf-8') as f:
                        self.documents.append(json.load(f))
            texts = [doc['title'] + ' ' + doc['content'] for doc in self.documents]
            self.embeddings = self.model.encode(texts, convert_to_tensor=True, show_progress_bar=True)
            with open(self.embedding_cache, 'wb') as f:
                pickle.dump((self.documents, self.embeddings), f)

    def search(self, query, top_k=5):
        query_emb = self.model.encode(query, convert_to_tensor=True)
        scores = util.cos_sim(query_emb, self.embeddings)[0]
        n_docs = len(self.documents)
        top_k = min(top_k, n_docs)
        top_results = np.argpartition(-scores, range(top_k))[:top_k]
        ranked = sorted([(self.documents[i], float(scores[i])) for i in top_results], key=lambda x: -x[1])
        return ranked
