import streamlit as st
from app.config import load_config
from app.rag_engine import RAGEngine
from app.ollama_interface import OllamaClient
import json

config = load_config()
ollama = OllamaClient()

st.set_page_config(page_title="SmartTour RAG", layout="centered")

# Custom CSS styling
st.markdown(
    """
    <style>
    .main {
        background-color: #f0f2f6;
    }
    .stChatMessage {
        background-color: #ffffff;
        border-radius: 10px;
        padding: 10px;
        margin-bottom: 10px;
    }
    </style>
""",
    unsafe_allow_html=True,
)

# Language selection
language = st.sidebar.selectbox(
    "Select Language",
    ["English", "Spanish", "French", "German", "Italian", "Portuguese"],
)

# Diccionario de textos por idioma
TEXTS = {
    "English": {
        "chat_input": "Say something to your travel assistant...",
        "select_model": "Select Language Model:",
        "select_model_help": "Choose the LLM model for responses.",
        "rag_checkbox": "Use RAG (Retrieval Augmented Generation)",
        "rag_checkbox_help": "Enable or disable retrieval augmented generation.",
        "spinner": "The assistant is writing...",
        "title": "🌍 Travel Planner Assistant"
    },
    "Spanish": {
        "chat_input": "Escribe algo a tu asistente de viajes...",
        "select_model": "Selecciona el modelo de lenguaje:",
        "select_model_help": "Elige el modelo LLM para las respuestas.",
        "rag_checkbox": "Usar RAG (Generación aumentada por recuperación)",
        "rag_checkbox_help": "Activa o desactiva la generación aumentada por recuperación.",
        "spinner": "El asistente está escribiendo...",
        "title": "🌍 Asistente de Planificación de Viajes"
    },
    "French": {
        "chat_input": "Dites quelque chose à votre assistant de voyage...",
        "select_model": "Sélectionnez le modèle de langue :",
        "select_model_help": "Choisissez le modèle LLM pour les réponses.",
        "rag_checkbox": "Utiliser RAG (Génération augmentée par récupération)",
        "rag_checkbox_help": "Activer ou désactiver la génération augmentée par récupération.",
        "spinner": "L'assistant écrit...",
        "title": "🌍 Assistant de Planification de Voyage"
    },
    "German": {
        "chat_input": "Sagen Sie etwas zu Ihrem Reiseassistenten...",
        "select_model": "Sprachmodell auswählen:",
        "select_model_help": "Wählen Sie das LLM-Modell für Antworten.",
        "rag_checkbox": "RAG verwenden (Retrieval Augmented Generation)",
        "rag_checkbox_help": "Aktivieren oder deaktivieren Sie die Retrieval Augmented Generation.",
        "spinner": "Der Assistent schreibt...",
        "title": "🌍 Reiseplanungsassistent"
    },
    "Italian": {
        "chat_input": "Parla con il tuo assistente di viaggio...",
        "select_model": "Seleziona il modello linguistico:",
        "select_model_help": "Scegli il modello LLM per le risposte.",
        "rag_checkbox": "Usa RAG (Generazione aumentata dal recupero)",
        "rag_checkbox_help": "Abilita o disabilita la generazione aumentata dal recupero.",
        "spinner": "L'assistente sta scrivendo...",
        "title": "🌍 Assistente Pianificazione Viaggi"
    },
    "Portuguese": {
        "chat_input": "Fale com seu assistente de viagens...",
        "select_model": "Selecione o modelo de linguagem:",
        "select_model_help": "Escolha o modelo LLM para as respostas.",
        "rag_checkbox": "Usar RAG (Geração aumentada por recuperação)",
        "rag_checkbox_help": "Ative ou desative a geração aumentada por recuperação.",
        "spinner": "O assistente está escrevendo...",
        "title": "🌍 Assistente de Planejamento de Viagens"
    }
}

st.title(TEXTS[language]["title"])

# Use st.session_state as a dict-like object for session state management
state = st.session_state

if "language" not in state:
    state["language"] = language
if state["language"] != language:
    state["language"] = language
    state["chat_history"] = []

# Session state initialization (use dict keys, not attributes)
if "chat_history" not in state:
    state["chat_history"] = []

# Chat interface
user_input = st.chat_input(TEXTS[language]["chat_input"])

# Modern controls in sidebar
selected_model = st.sidebar.selectbox(
    TEXTS[language]["select_model"],
    ollama.list_models(),
    format_func=lambda x: f"🤖 {x}",
    help=TEXTS[language]["select_model_help"],
)

use_rag = st.sidebar.checkbox(
    TEXTS[language]["rag_checkbox"],
    value=True,
    help=TEXTS[language]["rag_checkbox_help"],
)

# Display chat messages with alignment (always show chat history)
for msg in state["chat_history"]:
    if msg["role"] == "user":
        with st.chat_message("user"):
            st.markdown(
                f"""
                <div style='text-align: left;'>
                    {msg["content"]}
                </div>
                """,
                unsafe_allow_html=True
            )
    else:
        with st.chat_message("assistant"):
            st.markdown(
                f"""
                <div style='text-align: right;'>
                    {msg["content"]}
                </div>
                """,
                unsafe_allow_html=True
            )

# Chat input and streaming response
if user_input:
    # Show the user's message immediately (not yet in history)
    with st.chat_message("user"):
        st.markdown(
            f"""
            <div style='text-align: left;'>
                {user_input.strip()}
            </div>
            """,
            unsafe_allow_html=True
        )

    # Placeholder for streaming assistant message
    with st.chat_message("assistant"):
        assistant_placeholder = st.empty()
        streamed_text = ""
        engine = RAGEngine(config, use_rag)
        # Pasa el historial de conversación (sin el mensaje actual)
        chat_history = state["chat_history"].copy()
        with st.spinner(TEXTS[language]["spinner"]):
            for chunk in engine.stream_answer(
                user_input.strip(),
                selected_model,
                chat_history=chat_history
            ):
                if chunk.strip().startswith("{"):
                    try:
                        data = json.loads(chunk)
                        streamed_text += data.get("response", "")
                    except:
                        continue
                else:
                    streamed_text += chunk
                # Update the placeholder with the current streamed text
                assistant_placeholder.markdown(
                    f"""
                    <div style='text-align: right;'>
                        {streamed_text}
                    </div>
                    """,
                    unsafe_allow_html=True
                )
        # Add both user and assistant messages to history after displaying
        state["chat_history"].append({"role": "user", "content": user_input.strip()})
        state["chat_history"].append({"role": "assistant", "content": streamed_text})



