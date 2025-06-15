import streamlit as st
from app.config import load_config
from app.rag_engine import RAGEngine
from app.ollama_interface import OllamaClient
import json

config = load_config()
ollama = OllamaClient()

st.set_page_config(page_title="SmartTour RAG", layout="centered")

# Custom CSS for chat bubbles and modern controls
st.markdown("""
    <style>
    .chat-container {
        max-width: 600px;
        margin: auto;
        background: #f5f7fa;
        border-radius: 16px;
        padding: 24px 16px 8px 16px;
        box-shadow: 0 2px 16px rgba(0,0,0,0.07);
        min-height: 400px;
    }
    .msg-user {
        background: #e1ffc7;
        color: #222;
        padding: 10px 18px;
        border-radius: 18px 18px 4px 18px;
        margin: 8px 0 8px 0;
        max-width: 75%;
        text-align: left;
        float: left;
        clear: both;
        font-size: 1.05rem;
        box-shadow: 0 1px 3px rgba(0,0,0,0.04);
    }
    .msg-bot {
        background: #0084ff;
        color: #fff;
        padding: 10px 18px;
        border-radius: 18px 18px 18px 4px;
        margin: 8px 0 8px auto;
        max-width: 75%;
        text-align: left;
        float: right;
        clear: both;
        font-size: 1.05rem;
        box-shadow: 0 1px 3px rgba(0,0,0,0.09);
    }
    .input-bar {
        background: #fff;
        border-radius: 12px;
        box-shadow: 0 1px 6px rgba(0,0,0,0.06);
        padding: 12px 16px;
        margin-bottom: 0.5rem;
        display: flex;
        align-items: center;
    }
    .input-bar textarea {
        border: none !important;
        background: transparent !important;
        resize: none !important;
        font-size: 1.08rem;
        width: 100%;
        outline: none !important;
        box-shadow: none !important;
    }
    .send-btn {
        background: linear-gradient(90deg,#0084ff 60%,#00c6ff 100%);
        color: #fff;
        border: none;
        border-radius: 50%;
        width: 44px;
        height: 44px;
        font-size: 1.5rem;
        margin-left: 10px;
        cursor: pointer;
        transition: background 0.2s;
    }
    .send-btn:hover {
        background: linear-gradient(90deg,#0070e0 60%,#00b0e0 100%);
    }
    .modern-select, .modern-toggle {
        width: 100%;
        margin: 0.3rem 0 0.7rem 0;
        padding: 0.6rem 1rem;
        border-radius: 10px;
        border: 1px solid #d1d5db;
        background: #f1f5f9;
        font-size: 1.07rem;
        transition: border 0.2s;
    }
    .modern-select:focus, .modern-toggle:focus {
        border: 1.5px solid #0084ff;
        outline: none;
    }
    .modern-toggle {
        display: flex;
        align-items: center;
        justify-content: flex-start;
        gap: 0.7rem;
        cursor: pointer;
        font-weight: 500;
        background: #e0f7fa;
        border: 1.5px solid #00bcd4;
        color: #0084ff;
    }
    .modern-toggle input[type=checkbox] {
        accent-color: #0084ff;
        width: 1.2em;
        height: 1.2em;
        margin-right: 0.5em;
    }
    </style>
""", unsafe_allow_html=True)

st.markdown(f"<h2 style='text-align:center;margin-bottom:0.7em'>{config['ui']['title']}</h2>", unsafe_allow_html=True)

# Session state for chat history
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# Chat container (sin st.container())
# st.markdown('<div class="chat-container">', unsafe_allow_html=True)
for msg in st.session_state.chat_history:
    if msg["role"] == "user":
        st.markdown(f'<div class="msg-user">{msg["content"]}</div>', unsafe_allow_html=True)
    else:
        st.markdown(f'<div class="msg-bot">{msg["content"]}</div>', unsafe_allow_html=True)
st.markdown('<div style="clear:both"></div>', unsafe_allow_html=True)
st.markdown('</div>', unsafe_allow_html=True)

# Modern input bar and controls (sin st.container())
with st.form(key="chat_input_form", clear_on_submit=True):
    # st.markdown('<div class="input-bar">', unsafe_allow_html=True)
    user_input = st.text_area(
        "",
        placeholder="Escribe tu mensaje...",
        key="input_text",
        height=70,
        label_visibility="collapsed"
    )
    send_col, _ = st.columns([1, 8])
    with send_col:
        send_clicked = st.form_submit_button("➤", use_container_width=False)
    st.markdown('</div>', unsafe_allow_html=True)

    # Modern controls below input
    model_options = ollama.list_models()
    selected_model = st.selectbox(
        "Selecciona el modelo de lenguaje:",
        model_options,
        key="model_select",
        format_func=lambda x: f"🤖 {x}",
        help="Elige el modelo LLM para responder.",
    )
    st.markdown('<style>label[for="model_select"]{font-weight:600;}</style>', unsafe_allow_html=True)

    use_rag = st.checkbox(
        "Usar RAG (Recuperación aumentada)",
        value=True,
        key="rag_toggle",
        help="Activa o desactiva la recuperación aumentada.",
    )
    st.markdown('<style>label[for="rag_toggle"]{font-weight:600;}</style>', unsafe_allow_html=True)

if send_clicked and user_input.strip():
    # Añade mensaje del usuario
    st.session_state.chat_history.append({"role": "user", "content": user_input.strip()})

    # Procesa respuesta del modelo
    engine = RAGEngine(config, use_rag)
    response_chunks = []
    with st.spinner("El asistente está escribiendo..."):
        for chunk in engine.stream_answer(user_input.strip(), selected_model):
            if chunk.strip().startswith("{"):
                try:
                    data = json.loads(chunk)
                    response_chunks.append(data.get("response", ""))
                except:
                    continue
            else:
                response_chunks.append(chunk)
    response_text = "".join(response_chunks).strip()
    st.session_state.chat_history.append({"role": "bot", "content": response_text})

    # st.experimental_rerun()

