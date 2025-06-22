import streamlit as st
import json
from src.user_profile import UserProfile
from src.offer_loader import load_offers_from_directory
from src.recommender import Recommender
from src.utils import display_offer
from ollama_client import OllamaClient

# Session state
if "selected_recommendations" not in st.session_state:
    st.session_state.selected_recommendations = []

st.title("🌍 Smart Tourism Recommender")

st.sidebar.header("User Profile")
profile_input = st.sidebar.text_area("Paste User Profile JSON", height=300)

if profile_input:
    try:
        profile_json = json.loads(profile_input)
        if not isinstance(profile_json, dict):
            st.error("El perfil de usuario debe ser un objeto JSON (no una lista). Por favor, revisa el formato.")
            st.stop()
        user_profile = UserProfile(profile_json)
        offers = load_offers_from_directory("DATA")
        recommender = Recommender(user_profile, offers)
        top_offers = recommender.rank_offers()

        st.subheader("🎯 Top Recommendations")
        for score, offer in top_offers:
            with st.expander(f"{offer.raw.get('name') or offer.raw.get('title')} (Score: {score:.2f})"):
                st.markdown("\n".join(display_offer(offer.raw)))
                if st.button("Select", key=offer.raw.get("name") or offer.raw.get("title")):
                    st.session_state.selected_recommendations.append(offer.raw)

        if st.checkbox("🧠 Ask LLM to explain recommendations"):
            client = OllamaClient()
            prompt = f"Explain why these offers are good matches for the user: {profile_json}\n\nOffers:\n" + \
                     "\n".join([str(o.raw) for _, o in top_offers])
            explanation = ""
            for chunk in client.stream_generate("gemma:latest", prompt):
                explanation += chunk
                st.markdown(explanation)
    except Exception as e:
        st.error(f"Error parsing user profile: {e}")
