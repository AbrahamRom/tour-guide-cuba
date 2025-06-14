from app.ollama_interface import OllamaClient
from app.retriever import Retriever

class RAGEngine:
    def __init__(self, config, use_rag=True):
        self.use_rag = use_rag
        self.retriever = Retriever(config)
        self.ollama = OllamaClient()
        self.config = config

    def answer(self, query, model_name):
        docs = self.retriever.retrieve(query) if self.use_rag else []
        context = "\n".join(docs)
        prompt = f"""You are a friendly tourism assistant. Answer in the same language as the question.
        
Question: {query}
{f"Context:\n{context}" if context else ""}
Answer:"""
        return self.ollama.generate(
            model=model_name,
            prompt=prompt,
            temperature=self.config["llm"]["temperature"],
            max_tokens=self.config["llm"]["max_tokens"]
        )
