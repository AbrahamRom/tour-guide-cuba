from .ollama_interface import OllamaClient
from .ontology.retriever_ontology import OntologyRetriever
from .fallback_scraper import search_dynamic
from sentence_transformers import SentenceTransformer
import faiss
import numpy as np

class RAGEngine:
    def __init__(self, config, use_rag=True):
        self.use_rag = use_rag
        # Comprobación de la clave 'ontology'
        ontology_path = config.get("ontology", {}).get("owl_path", "modules/src/rag/data/tourism.owl")
        self.ontology_retriever = OntologyRetriever({"ontology": {"owl_path": ontology_path}})
        self.ollama = OllamaClient()
        self.config = config
        self.embedder = SentenceTransformer(config["retriever"]["model"])  # Añadido para embeddings

    def build_prompt(self, query, chat_history, action_tag=None):
        context = ""
        force_search = False
        summarize = False
        if action_tag == "search":
            force_search = True
        if action_tag == "summarize":
            summarize = True
            
        if self.use_rag or force_search:
            # Solo búsqueda en ontología
            ontology_results = []
            
            # Siempre buscar en ontología, no en documentos tradicionales
            ontology_results = self.ontology_retriever.retrieve(query)
            
            # Resultados
            all_results = ontology_results
            
            if all_results:
                context = "\n".join(all_results)
            else:
                # Fallback a scraping dinámico
                ecured_fallback = search_dynamic(query)
                if ecured_fallback:
                    context = ecured_fallback
                    # Insertar conocimiento en ontología para futuras consultas
                    from .ontology.ontology_manager import OntologyManager
                    ontology_manager = OntologyManager(self.config["ontology"]["owl_path"])
                    ontology_manager.insert_fallback_knowledge(
                        name=query, 
                        province="Unknown", 
                        description=context
                    )

       
        history_text = ""
        if chat_history:
            # Extraer solo el contenido de cada turno
            contents = [turn.get("content", "") for turn in chat_history]
            if contents:
                # Calcular embeddings
                query_emb = self.embedder.encode([query])
                history_embs = self.embedder.encode(contents)

                # Normalizar para similitud por coseno
                query_emb = query_emb / np.linalg.norm(query_emb, axis=1, keepdims=True)
                history_embs = history_embs / np.linalg.norm(history_embs, axis=1, keepdims=True)

                # Crear índice FAISS para similitud por coseno (IndexFlatIP)
                index = faiss.IndexFlatIP(history_embs.shape[1])
                index.add(history_embs.astype(np.float32))
                D, I = index.search(query_emb.astype(np.float32), min(10, len(contents)))
                top_indices = I[0]

                # Formatear solo los mensajes más similares
                formatted_history = []
                for idx in top_indices:
                    turn = chat_history[idx]
                    role = turn.get("role", "user")
                    content = turn.get("content", "")
                    formatted_history.append(f"{role.capitalize()}: {content}")
                history_text = "\n".join(formatted_history)
       

        important_note = ""
        if action_tag == "important":
            important_note = "\n[The last user message is marked as IMPORTANT. Prioritize this information in your answer.]"
        summarize_note = ""
        if summarize:
            summarize_note = "\n[Summarize the conversation so far. Provide a concise summary.]"

        prompt = f"""You are a warm and helpful tourism assistant. Answer in the same language as the question.
Take into account the previous conversation in the chat_history field, as the user may refer to information already provided.{important_note}{summarize_note}

{f"Chat History:\n{history_text}\n" if history_text else ""}
Question: {query}
{f"Context:\n{context}" if context else ""}
Answer:"""
        return prompt

    def stream_answer(self, query, model_name, chat_history=None, action_tag=None):
        prompt = self.build_prompt(query, chat_history, action_tag=action_tag)
        return self.ollama.stream_generate(
            model=model_name,
            prompt=prompt,
            temperature=self.config["llm"]["temperature"],
            max_tokens=self.config["llm"]["max_tokens"],
        )
        prompt = self.build_prompt(query, chat_history, action_tag=action_tag)
        return self.ollama.stream_generate(
            model=model_name,
            prompt=prompt,
            temperature=self.config["llm"]["temperature"],
            max_tokens=self.config["llm"]["max_tokens"],
        )
