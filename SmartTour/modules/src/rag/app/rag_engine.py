from app.ollama_interface import OllamaClient
from app.retriever import Retriever
from app.fallback_scraper import search_ecured

class RAGEngine:
    def __init__(self, config, use_rag=True):
        self.use_rag = use_rag
        self.retriever = Retriever(config)
        self.ollama = OllamaClient()
        self.config = config

    def build_prompt(self, query):
        docs = self.retriever.retrieve(query) if self.use_rag else []
        context = "\n".join(docs)
        prompt = f"""You are a friendly tourism assistant. Answer only in the same language as the question.

Question: {query}
{f"Context:\n{context}" if context else ""}
Answer:"""
        return prompt
    
    def build_prompt(self, query):
        context = ""
        if self.use_rag:
            docs = self.retriever.retrieve(query)
            if docs:
                context = "\n".join(docs)
            else:
                ecured_fallback = search_ecured(query)
                if ecured_fallback:
                    context = ecured_fallback

        prompt = f"""You are a warm and helpful tourism assistant. Answer in the same language as the question.

Question: {query}
{f"Context:\n{context}" if context else ""}
Answer:"""
        return prompt

    def stream_answer(self, query, model_name, chat_history=None):
        prompt = self.build_prompt(query)
        return self.ollama.stream_generate(
            model=model_name,
            prompt=prompt,
            temperature=self.config["llm"]["temperature"],
            max_tokens=self.config["llm"]["max_tokens"],
            chat_history=chat_history
        )
