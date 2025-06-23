import streamlit as st
from .rag_sim import simulate_rag_interaction
from .mock_queries import queries

def render_rag_simulator():
    st.title("📚 RAG Chatbot Simulation")

    selected_model = st.selectbox("Select model", [ "openhermes", "gemma2"])
    use_rag = st.checkbox("Use RAG (Retrieve from KB)", value=True)
    show_details = st.checkbox("Show individual responses", value=True)

    results = []
    if st.button("▶️ Run Simulation"):
        for query in queries:
            result = simulate_rag_interaction(query, model=selected_model, use_rag=use_rag)
            results.append(result)

        st.success("Simulation complete!")
        avg_latency = sum(r["latency"] for r in results) / len(results)
        avg_length = sum(r["length"] for r in results) / len(results)

        st.metric("⏱️ Average Latency", f"{avg_latency:.2f} sec")
        st.metric("📝 Avg. Response Length", f"{avg_length:.1f} words")
        sources = set(r["source"] for r in results)
        st.markdown(f"**Sources used:** {', '.join(sources)}")

        if show_details:
            for r in results:
                st.markdown(f"""
                ---  
                **Query**: {r["query"]}  
                **Response**: {r["response"][:300]}{"..." if len(r["response"]) > 300 else ""}  
                **Source**: `{r["source"]}`  
                **Latency**: `{r["latency"]} sec`  
                """)
