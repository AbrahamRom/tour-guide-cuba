import streamlit as st
from simulator.rag_sim_ui import render_rag_simulator
from simulator.chatbot_sim_ui import render_chatbot_simulator
from simulator.searcher_sim_ui import render_search_simulator
from simulator.planner_sim_ui import render_planner_simulator
from simulator.recommender_sim_ui import render_recommender_simulator

def render():
    st.set_page_config(page_title="🧪 Simulation Dashboard", layout="wide")
    st.title("🧠 Multi-Agent Tourism System Simulation")

    module = st.sidebar.radio("Select Subsystem to Simulate", [
        "Chatbot",
        "Recommender",
        "Planner",
        "Semantic Searcher",
        "RAG Assistant"
    ])

    if module == "Chatbot":
        render_chatbot_simulator()
    elif module == "Recommender":
        render_recommender_simulator()
    elif module == "Planner":
        render_planner_simulator()
    elif module == "Semantic Searcher":
        render_search_simulator()
    elif module == "RAG Assistant":
        render_rag_simulator()
