import time
import json
from modules.src.rag.app.rag_engine import RAGEngine
from modules.src.rag.app.config import load_config

config = load_config()

def simulate_rag_interaction(query, model, use_rag=True, chat_history=None, action_tag=None):
    engine = RAGEngine(config, use_rag)
    prompt = engine.build_prompt(query, chat_history or [], action_tag)

    response = ""
    start = time.time()
    source = "unknown"

    for chunk in engine.stream_answer(query, model, chat_history=chat_history or [], action_tag=action_tag):
        try:
            data = json.loads(chunk)
            chunk_text = data.get("response", "")
        except:
            chunk_text = chunk
        response += chunk_text
    end = time.time()

    # Detección básica de origen (fallback Wikipedia si no hay docs en KB)
    if "wikipedia.org" in prompt.lower() or "ecured" in prompt.lower():
        source = "Wikipedia"
    elif "Context:\n" in prompt:
        source = "Knowledge Base"
    else:
        source = "None"

    return {
        "query": query,
        "response": response.strip(),
        "latency": round(end - start, 2),
        "source": source,
        "length": len(response.split()),
        "use_rag": use_rag,
        "action_tag": action_tag
    }
