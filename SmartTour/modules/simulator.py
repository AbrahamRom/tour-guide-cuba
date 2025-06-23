import streamlit as st
from .simulation.rag.rag_sim_ui import render_rag_simulator
from .simulation.chatbot.chatbot_sim_ui import render_chatbot_simulator
from .simulation.searcher.searcher_sim_ui import render_search_simulator
from .simulation.planner.planner_sim_ui import render_planner_simulator
from .simulation.recommender.recommender_sim_ui import render_recommender_simulator

def render(state):
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