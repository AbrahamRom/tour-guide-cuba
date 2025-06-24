import streamlit as st
from .rag_sim import simulate_rag_interaction
from .mock_queries import queries
import pandas as pd
import io
import json

def render_rag_simulator():
    st.title("📚 RAG Chatbot Simulation")

    selected_model = st.selectbox("Select model", [ "openhermes", "gemma2"])
    use_rag = st.checkbox("Use RAG (Retrieve from KB)", value=True)
    show_details = st.checkbox("Show individual responses", value=True)

    results = []
    connection_error = False  # Track if any connection error occurs
    if st.button("▶️ Run Simulation"):
        for query in queries:
            result = simulate_rag_interaction(query, model=selected_model, use_rag=use_rag)
            if result.get("source") == "ConnectionError":
                connection_error = True
            results.append(result)

        if connection_error:
            st.error("❌ Connection error: Unable to reach HuggingFace or required model. Please check your internet connection or try again later.")
            # Optionally, skip further processing if all queries failed
            if all(r.get("source") == "ConnectionError" for r in results):
                return

        st.success("Simulation complete!")
        avg_latency = sum(r["latency"] for r in results) / len(results)
        avg_length = sum(r["length"] for r in results) / len(results)

        st.metric("⏱️ Average Latency", f"{avg_latency:.2f} sec")
        st.metric("📝 Avg. Response Length", f"{avg_length:.1f} words")
        sources = set(r["source"] for r in results)
        st.markdown(f"**Sources used:** {', '.join(sources)}")


        # Prepare DataFrame for download
        df = pd.DataFrame(results)
        csv_buffer = io.StringIO()
        df.to_csv(csv_buffer, index=False)
        csv_data = csv_buffer.getvalue()

        st.download_button(
            label="⬇️ Download Results as CSV",
            data=csv_data,
            file_name="rag_simulation_results.csv",
            mime="text/csv"
        )

        if show_details:
            for r in results:
                st.markdown(f"""
                ---  
                **Query**: {r["query"]}  
                **Response**: {r["response"][:300]}{"..." if len(r["response"]) > 300 else ""}  
                **Source**: `{r["source"]}`  
                **Latency**: `{r["latency"]} sec`  
                """)

        # Add JSON download button
        json_data = json.dumps(results, ensure_ascii=False, indent=2)
        st.download_button(
            label="⬇️ Download Results as JSON",
            data=json_data,
            file_name="rag_simulation_results.json",
            mime="application/json"
        )
