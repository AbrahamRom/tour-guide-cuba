import streamlit as st
from simulator.chatbot_sim import run_chatbot_simulation
from simulator.mock_profiles import sample_profile

def render_simulation_ui():
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
