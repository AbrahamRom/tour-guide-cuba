# simulator/searcher_sim.py
import time
from modules.src.searcher.app.retriever import Retriever
from modules.src.searcher.app.query_corrector import suggest_query
import ir_datasets

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


def evaluate_searcher_with_dataset(top_k=10, correct=True, max_queries=30):
    dataset = ir_datasets.load("cranfield")
    queries = list(dataset.queries_iter())
    qrels = {qrel.query_id: set() for qrel in dataset.qrels_iter()}
    for qrel in dataset.qrels_iter():
        qrels[qrel.query_id].add(qrel.doc_id)
    docs = {doc.doc_id: doc for doc in dataset.docs_iter()}

    results = []
    n_eval = min(max_queries, len(queries))
    for q in queries[:n_eval]:
        relevant_docs = qrels.get(q.query_id, set())
        # Simular búsqueda
        res = simulate_search_query(q.text, correct=correct, top_k=top_k)
        # Obtener doc_ids de los resultados (requiere que retriever devuelva doc_id)
        # Suponemos que retriever.search devuelve [(doc, score), ...] y doc tiene 'doc_id'
        retrieved = [r[0]['doc_id'] for r in retriever.search(res['corrected_query'], top_k=top_k)]
        retrieved_set = set(retrieved)
        true_positives = len(retrieved_set & relevant_docs)
        precision = true_positives / len(retrieved_set) if retrieved_set else 0.0
        recall = true_positives / len(relevant_docs) if relevant_docs else 0.0
        f1 = 2 * precision * recall / (precision + recall) if (precision + recall) else 0.0
        results.append({
            "query_id": q.query_id,
            "precision": precision,
            "recall": recall,
            "f1": f1,
            "latency": res["latency"]
        })
    avg_precision = sum(r["precision"] for r in results) / n_eval
    avg_recall = sum(r["recall"] for r in results) / n_eval
    avg_f1 = sum(r["f1"] for r in results) / n_eval
    avg_latency = sum(r["latency"] for r in results) / n_eval
    return {
        "average_precision": avg_precision,
        "average_recall": avg_recall,
        "average_f1": avg_f1,
        "average_latency": avg_latency,
        "details": results
    }
