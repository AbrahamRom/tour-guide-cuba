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

st.sidebar.header("Upload User Profile")

uploaded_file = st.sidebar.file_uploader("Upload a JSON file with user profile", type="json")

if uploaded_file is not None:
    try:
        profile_json = json.load(uploaded_file)
        user_profile = UserProfile(profile_json)
        offers = load_offers_from_directory("DATA")
        recommender = Recommender(user_profile, offers)
        top_offers = recommender.rank_offers()
        if not top_offers:
            st.warning("No matching offers found or offer data is invalid.")
        else:    
            st.subheader("🎯 Top Recommendations")
            for score, offer in top_offers:
                with st.expander(f"{offer.raw.get('name') or offer.raw.get('title')} (Score: {score:.2f})"):
                    st.markdown("\n".join(display_offer(offer.raw)))
                    if st.button("Select", key=offer.raw.get("name") or offer.raw.get("title")):
                        st.session_state.selected_recommendations.append(offer.raw)

        # List available Ollama models and let user choose
        client = OllamaClient()
        models_response = client.list_models()
        # Handle both list and dict response for compatibility
        if isinstance(models_response, dict) and "models" in models_response:
            models = models_response["models"]
        else:
            models = models_response
        # Safely extract model names whether models are dicts or strings
        model_names = [
            model["name"] if isinstance(model, dict) and "name" in model else str(model)
            for model in models
        ]
        selected_model = st.selectbox(
            "Choose LLM model",
            model_names,
            index=0 if "gemma:latest" not in model_names else model_names.index("gemma:latest")
        )

        if st.checkbox("🧠 Ask LLM to explain recommendations"):
            prompt = f"Explain why these offers are good matches for the user: {profile_json}\n\nOffers:\n" + \
                 "\n".join([str(o.raw) for _, o in top_offers])
            explanation = ""
            response_placeholder = st.empty()
            for chunk in client.stream_generate(selected_model, prompt):
                # Si el chunk es JSON, extrae solo el campo "response"
                try:
                    if isinstance(chunk, str):
                        data = json.loads(chunk)
                    else:
                        data = chunk
                    text = data.get("response", "")
                except Exception:
                    text = str(chunk)
                explanation += text
                response_placeholder.markdown(explanation)

    except Exception as e:
        st.error(f"Error reading or processing the uploaded file: {e}")
else:
    st.info("Please upload a user profile JSON file.")
