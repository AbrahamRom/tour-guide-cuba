# simulator/searcher_sim.py
import time
from modules.src.searcher.app.retriever import Retriever
from modules.src.searcher.app.query_corrector import suggest_query

retriever = Retriever()


def simulate_search_query(query, correct=True, top_k=10):
    corrected = suggest_query(query, [doc['title'] for doc in retriever.documents]) if correct else query

    start = time.time()
    results = retriever.search(corrected, top_k=top_k)
    end = time.time()

    return {
        "query": query,
        "corrected_query": corrected,
        "latency": round(end - start, 3),
        "num_results": len(results),
        "top_score": results[0][1] if results else 0.0,
        "titles": [r[0]['title'] for r in results[:3]]
    }
