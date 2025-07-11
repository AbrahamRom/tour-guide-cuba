def average(values):
    return sum(values) / len(values) if values else 0.0

def summarize_results(results):
    return {
        "avg_latency": average([r["latency"] for r in results if "latency" in r]),
        "top_titles": [r.get("title") for r in results[:3] if "title" in r]
    }
