import streamlit as st
from .chatbot_sim import run_chatbot_simulation, evaluate_extraction_quality
from .mock_profiles import sample_profile
import json

def render_chatbot_simulator():
    st.title("🤖 Chatbot Simulation")
    if st.button("Run Simulation"):
        logs, data = run_chatbot_simulation(sample_profile)
        st.success("Simulation completed!")

        st.subheader("Collected Travel Data")
        st.json(data)

        st.subheader("Detailed Logs")
        for entry in logs:
            st.markdown(f"""
            **Field:** {entry['field']}  
            **User Input:** {entry['user_input']}  
            **Bot Response:** {entry['bot_response']}  
            **Extracted Value:** {entry['value_extracted']}  
            **Latency:** `{entry['latency']} sec`  
            """)

        avg_latency = sum(l["latency"] for l in logs) / len(logs)
        st.metric("⏱️ Average Latency", f"{avg_latency:.2f} s")

        st.download_button("📥 Download Results", data=str(logs), file_name="chatbot_simulation.json")

    if st.button("Evaluate Extraction Quality (30 runs)"):
        with st.spinner("Evaluating extraction quality..."):
            results = evaluate_extraction_quality(30)
        st.success("Evaluation completed!")
        st.metric("Average Cosine Similarity", f"{results['average_cosine_similarity']:.3f}")
        st.metric("Average Latency (s)", f"{results['average_latency']:.2f}")
        st.write("All Similarities:", results["all_similarities"])
        st.write("All Latencies:", results["all_latencies"])

        st.download_button(
            "📥 Download Evaluation Results",
            data=json.dumps(results, indent=2),
            file_name="evaluation_results.json",
            mime="application/json"
        )
