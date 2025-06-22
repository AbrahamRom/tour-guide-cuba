# simulator/searcher_sim_ui.py
import streamlit as st
from simulator.searcher_sim import simulate_search_query
from simulator.searcher_queries import search_queries

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
