import streamlit as st
from .src.rag.app.config import load_config
from .src.rag.app.rag_engine import RAGEngine
from .src.rag.app.ollama_interface import OllamaClient
import json

config = load_config()
ollama = OllamaClient()

def render(state):

    # Custom CSS styling for chat bubbles
    st.markdown(
        """
        <style>
        .main {
            background-color: #f0f2f6;
        }
        .chat-bubble-user {
            background-color: #e6f0fa;
            color: #222;
            border-radius: 18px 18px 18px 4px;
            padding: 12px 18px;
            margin-bottom: 8px;
            max-width: 70%;
            display: inline-block;
            text-align: left;
            box-shadow: 0 1px 2px rgba(0,0,0,0.04);
        }
        .chat-bubble-assistant {
            background-color: #f5f5f5;
            color: #222;
            border-radius: 18px 18px 4px 18px;
            padding: 12px 18px;
            margin-bottom: 8px;
            max-width: 70%;
            display: inline-block;
            text-align: left;
            box-shadow: 0 1px 2px rgba(0,0,0,0.04);
        }
        .chat-row {
            display: flex;
            align-items: flex-end;
            margin-bottom: 2px;
        }
        .chat-row-user {
            justify-content: flex-start;
        }
        .chat-row-assistant {
            justify-content: flex-end;
        }
        .chat-avatar {
            width: 36px;
            height: 36px;
            border-radius: 50%;
            margin: 0 8px;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 22px;
            background: #fff;
            border: 1px solid #eee;
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

    if "language" not in state:
        state["language"] = language
    if state["language"] != language:
        state["language"] = language
        state["chat_history_KB"] = []

    # Session state initialization (use dict keys, not attributes)
    if "chat_history_KB" not in state:
        state["chat_history_KB"] = []

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

    # Mostrar historial de chat con burbujas y avatares
    for msg in state["chat_history_KB"]:
        if msg["role"] == "user":
            st.markdown(
                f"""
                <div class="chat-row chat-row-user">
                    <div class="chat-avatar">🧑</div>
                    <div class="chat-bubble-user">{msg["content"]}</div>
                </div>
                """,
                unsafe_allow_html=True
            )
        else:
            st.markdown(
                f"""
                <div class="chat-row chat-row-assistant">
                    <div style="flex:1"></div>
                    <div class="chat-bubble-assistant">{msg["content"]}</div>
                    <div class="chat-avatar">🤖</div>
                </div>
                """,
                unsafe_allow_html=True
            )

    # Chat input and streaming response
    if user_input:
        # Mostrar mensaje del usuario inmediatamente
        st.markdown(
            f"""
            <div class="chat-row chat-row-user">
                <div class="chat-avatar">🧑</div>
                <div class="chat-bubble-user">{user_input.strip()}</div>
            </div>
            """,
            unsafe_allow_html=True
        )

        # Placeholder para la respuesta del asistente
        assistant_placeholder = st.empty()
        streamed_text = ""
        engine = RAGEngine(config, use_rag)
        chat_history = state["chat_history_KB"].copy()
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
                assistant_placeholder.markdown(
                    f"""
                    <div class="chat-row chat-row-assistant">
                        <div style="flex:1"></div>
                        <div class="chat-bubble-assistant">{streamed_text}</div>
                        <div class="chat-avatar">🤖</div>
                    </div>
                    """,
                    unsafe_allow_html=True
                )
        state["chat_history_KB"].append({"role": "user", "content": user_input.strip()})
        state["chat_history_KB"].append({"role": "assistant", "content": streamed_text})





