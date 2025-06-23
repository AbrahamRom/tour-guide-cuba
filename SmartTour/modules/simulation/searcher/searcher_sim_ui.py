# simulator/searcher_sim_ui.py
import streamlit as st
from .searcher_sim import simulate_search_query, evaluate_searcher_with_dataset
from .searcher_queries import search_queries

def render_search_simulator():
    st.title("🔍 Document Search Simulation")

    correct = st.checkbox("Enable spelling correction", value=True)
    top_k = st.slider("Top-K results", min_value=1, max_value=20, value=10)
    show_details = st.checkbox("Show individual result summaries", value=True)

    if st.button("▶️ Run Simulation"):
        results = [simulate_search_query(q, correct=correct, top_k=top_k) for q in search_queries]

        st.success("Simulation complete!")

        avg_latency = sum(r["latency"] for r in results) / len(results)
        avg_results = sum(r["num_results"] for r in results) / len(results)

        st.metric("⏱️ Avg. Latency", f"{avg_latency:.2f} s")
        st.metric("📄 Avg. Results", f"{avg_results:.1f} docs")

        if show_details:
            for r in results:
                st.markdown(f"""
                ---
                **Query:** {r['query']}  
                **Corrected:** {r['corrected_query']}  
                **Latency:** `{r['latency']} s`  
                **Top Titles:** {', '.join(r['titles'])}  
                **Top Score:** `{r['top_score']:.2f}`
                """)

    if st.button("Evaluate with Cranfield Dataset"):
        with st.spinner("Evaluating searcher with Cranfield dataset..."):
            metrics = evaluate_searcher_with_dataset(top_k=top_k, correct=correct, max_queries=30)
        st.success("Evaluation complete!")
        st.metric("Precision", f"{metrics['average_precision']:.3f}")
        st.metric("Recall", f"{metrics['average_recall']:.3f}")
        st.metric("F1", f"{metrics['average_f1']:.3f}")
        st.metric("Avg. Latency", f"{metrics['average_latency']:.2f} s")
        st.write("Details:", metrics["details"])
