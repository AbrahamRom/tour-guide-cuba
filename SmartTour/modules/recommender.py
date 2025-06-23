import streamlit as st
import json
from .src.recommender.src.user_profile import UserProfile
from .src.recommender.src.offer_loader import load_offers_from_directory
from .src.recommender.src.recommender import Recommender
from .src.recommender.src.utils import display_offer
from .src.rag.app.ollama_interface import OllamaClient

def render(state):
    # Session state
    if "selected_recommendations" not in state:
        state["selected_recommendations"] = []

    st.markdown(
        """
        <style>
        .main-title {font-size:2.5em; font-weight:bold; color:#2E8B57;}
        .subtitle {font-size:1.2em; color:#555;}
        .recommendation-card {background:#f8f9fa; border-radius:10px; padding:1em; margin-bottom:1em;}
        .stButton>button {background-color:#2E8B57; color:white;}
        </style>
        """,
        unsafe_allow_html=True
    )

    st.markdown('<div class="main-title">🌴 SmartTour Cuba - Recommender</div>', unsafe_allow_html=True)
    st.markdown('<div class="subtitle">Descubre las mejores experiencias personalizadas en Cuba</div>', unsafe_allow_html=True)
    st.sidebar.header("👤 Subir Perfil de Usuario")

    uploaded_file = st.sidebar.file_uploader(
        "Sube un archivo JSON con el perfil del usuario",
        type="json",
        help="El archivo debe contener las preferencias y datos del usuario."
    )

    st.sidebar.markdown("---")
    st.sidebar.markdown("¿No tienes un perfil? Usa este ejemplo:")
    st.sidebar.code('{"name": "Ana", "interests": ["playa", "historia"], "budget": "medio"}', language="json")

    # LLM model and language selection in sidebar
    st.sidebar.markdown("---")
    st.sidebar.markdown("### 🤖 Configuración del LLM")
    client = OllamaClient()
    models_response = client.list_models()
    if isinstance(models_response, dict) and "models" in models_response:
        models = models_response["models"]
    else:
        models = models_response
    model_names = [
        model["name"] if isinstance(model, dict) and "name" in model else str(model)
        for model in models
    ]
    selected_model = st.sidebar.selectbox(
        "Elige el modelo LLM",
        model_names,
        index=0 if "gemma:latest" not in model_names else model_names.index("gemma:latest"),
        help="Selecciona el modelo de lenguaje para la explicación."
    )
    language = st.sidebar.selectbox(
        "Idioma de la explicación",
        ["Español", "English"],
        index=0,
        help="Selecciona el idioma en el que deseas la explicación."
    )

    prompt_placeholder = {
        "Español": (
            "De las siguientes ofertas, indica cuáles son buenas o ideales para el usuario y por qué, "
            "y también cuáles no son convenientes y por qué. Sé específico en tu explicación."
        ),
        "English": (
            "From the following offers, indicate which ones are good or ideal for the user and why, "
            "and also which ones are not suitable and why. Be specific in your explanation."
        )
    }

    if uploaded_file is not None:
        try:
            profile_json = json.load(uploaded_file)
            user_profile = UserProfile(profile_json)
            offers = load_offers_from_directory("../DATA")
            recommender = Recommender(user_profile, offers)
            top_offers = recommender.rank_offers()
            if not top_offers:
                st.warning("No matching offers found or offer data is invalid.")
            else:
                st.subheader("🎯 Recomendaciones Principales")
                offer_keys = []
                offer_objs = []
                for idx, (score, offer) in enumerate(top_offers):
                    offer_title = offer.raw.get('name') or offer.raw.get('title')
                    offer_key = f"offer_{idx}_{offer_title}"
                    offer_keys.append(offer_key)
                    offer_objs.append(offer)
                    with st.expander(f"{offer_title} (Puntaje: {score:.2f})"):
                        # Muestra los campos de la oferta de forma estilizada sin particularizar nombres
                        details = ""
                        for k, v in offer.raw.items():
                            details += f"<b>{k.capitalize()}:</b> {v}<br>"
                        st.markdown(
                            f'<div class="recommendation-card">{details}</div>',
                            unsafe_allow_html=True
                        )

                # LLM automatic explanation with spinner
                st.markdown("### 🤖 ¿Qué es lo mejor para ti?")
                prompt = (
                    f"{prompt_placeholder[language]}\n\nPerfil de usuario:\n{profile_json}\n\nOfertas:\n" +
                    "\n".join([str(o.raw) for o in offer_objs])
                )
                explanation = ""
                explanation_placeholder = st.empty()
                with st.spinner("El modelo LLM está generando la explicación..."):
                    # Intenta imprimir cada chunk directamente para debug
                    for chunk in client.stream_generate(selected_model, prompt):
                        try:
                            # Si el chunk es texto plano, úsalo directamente
                            if isinstance(chunk, str):
                                try:
                                    # Intenta decodificar como JSON, si falla, es texto plano
                                    data = json.loads(chunk)
                                    text = data.get("response", "")
                                    if not text:
                                        text = chunk
                                except Exception:
                                    text = chunk
                            else:
                                # Si es dict, busca el campo 'response'
                                text = chunk.get("response", str(chunk))
                        except Exception:
                            text = str(chunk)
                        explanation += text
                        explanation_placeholder.markdown(explanation)
                # Si no se imprimió nada, muestra un mensaje de error
                if not explanation.strip():
                    explanation_placeholder.error("No se recibió explicación del modelo. Verifica que el modelo esté funcionando correctamente o revisa la conexión.")

                # User selects offers with checkboxes (only after LLM finishes)
                st.markdown("### ✅ Selecciona las ofertas que te interesan")
                selected = []
                for offer_key, offer in zip(offer_keys, offer_objs):
                    checked = st.checkbox(
                        offer.raw.get('name') or offer.raw.get('title'),
                        key=offer_key
                    )
                    if checked:
                        selected.append(offer.raw)
                state["selected_recommendations"] = selected

        except Exception as e:
            st.error(f"Error leyendo o procesando el archivo subido: {e}")
    else:
        st.info("Por favor, sube un archivo JSON con el perfil del usuario para comenzar.")

