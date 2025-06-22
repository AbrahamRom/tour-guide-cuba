# simulator/recommender_sim_ui.py
import streamlit as st
from simulator.recommender_sim import simulate_recommendation
from simulator.recommender_profiles import sample_profiles


def render_recommender_simulator():
    st.title("🎯 Recommender Simulation")

    offers_dir = st.text_input("Offers Directory", "../DATA")
    top_k = st.slider("Top-K Recommendations", 1, 10, 5)

    if st.button("▶️ Run Simulation"):
        for path in sample_profiles:
            try:
                result = simulate_recommendation(path, offers_dir, top_k)
                st.success(f"Profile: {result['profile_name']}")
                st.write(f"Total Offers Loaded: {result['num_offers']}")
                st.markdown("**Top Recommendations:**")
                for r in result["recommendations"]:
                    st.markdown(f"- **{r['title']}** (Score: {r['score']})")
            except Exception as e:
                st.error(f"❌ Error processing {path}: {e}")
