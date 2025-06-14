import json

def load_knowledge_base(path="../data/knowledge_base.json"):
    with open(path, "r") as f:
        return json.load(f)

def retrieve(query, kb):
    # Placeholder: return all docs containing the query as substring
    return [doc for doc in kb if query.lower() in doc["content"].lower()]
