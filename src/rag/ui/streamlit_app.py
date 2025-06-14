import streamlit as st
from app.config import load_config
from app.rag_engine import answer_query
from app.utils import format_answer

st.title("Tourism RAG Assistant")

config = load_config()

query = st.text_input("Ask a tourism-related question:")

if query:
    answer = answer_query(query, config)
    st.write(format_answer(answer))
