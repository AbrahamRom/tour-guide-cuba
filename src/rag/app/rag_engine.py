from .retriever import load_knowledge_base, retrieve
from .ollama_interface import query_ollama

def answer_query(query, config):
    kb = load_knowledge_base(config.get("knowledge_base_path", "../data/knowledge_base.json"))
    docs = retrieve(query, kb)
    context = "\n".join([doc["content"] for doc in docs])
    prompt = f"Context:\n{context}\n\nQuestion: {query}\nAnswer:"
    return query_ollama(prompt, config)
