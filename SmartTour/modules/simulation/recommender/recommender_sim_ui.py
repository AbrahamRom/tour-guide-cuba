# simulator/recommender_sim_ui.py
import streamlit as st
from .recommender_sim import simulate_recommendation
from .recommender_profiles import sample_profiles
import json


def render_recommender_simulator():
    st.title("🎯 Recommender Simulation")

    offers_dir = st.text_input("Offers Directory", "../DATA")
    top_k = st.slider("Top-K Recommendations", 1, 10, 5)

    if st.button("▶️ Run Simulation"):
        all_results = []
        num_success = 0
        num_fail = 0
        total_offers = 0
        total_scores = 0
        total_recommendations = 0

        for path in sample_profiles:
            try:
                result = simulate_recommendation(path, offers_dir, top_k)
                all_results.append(result)
                num_success += 1
                total_offers += result["num_offers"]
                scores = [r["score"] for r in result["recommendations"]]
                total_scores += sum(scores)
                total_recommendations += len(scores)
                st.success(f"Profile: {result['profile_name']}")
                st.write(f"Total Offers Loaded: {result['num_offers']}")
                st.markdown("**Top Recommendations:**")
                for r in result["recommendations"]:
                    st.markdown(f"- **{r['title']}** (Score: {r['score']})")
            except Exception as e:
                num_fail += 1
                st.error(f"❌ Error processing {path}: {e}")

        if num_success > 0:
            avg_offers = total_offers / num_success
            avg_score = total_scores / total_recommendations if total_recommendations else 0
            st.info(f"✅ Profiles processed: {num_success}")
            st.info(f"❌ Profiles failed: {num_fail}")
            st.metric("Avg. Offers Loaded", f"{avg_offers:.1f}")
            st.metric("Avg. Recommendation Score", f"{avg_score:.3f}")
            st.metric("Total Recommendations", f"{total_recommendations}")

            json_data = json.dumps(all_results, indent=2, ensure_ascii=False)
            st.download_button(
                label="📥 Download All Results (JSON)",
                data=json_data,
                file_name="recommender_simulation_results.json",
                mime="application/json"
            )
        else:
            st.warning("No profiles processed successfully.")
