import streamlit as st
from app.config import load_config
from app.rag_engine import RAGEngine
from app.ollama_interface import OllamaClient



config = load_config()
ollama = OllamaClient()

st.set_page_config(page_title="SmartTour RAG", layout="centered")
st.title(config["ui"]["title"])

model_options = ollama.list_models()
selected_model = st.selectbox("Select LLM model:", model_options)

use_rag = st.checkbox("Enable RAG (Retrieval-Augmented Generation)", value=True)

query = st.text_area("Ask me anything about tourism or local culture:")

if st.button("Get Answer"):
    if query.strip() == "":
        st.warning("Please enter a question.")
    else:
        engine = RAGEngine(config, use_rag)
        answer = engine.answer(query, selected_model)
        st.success("Answer:")
        st.write(answer)
