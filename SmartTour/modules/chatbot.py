import sys
import os

import streamlit as st

from .src.chatbot.bot import (
    initialize_conversation,
    chatbot_conversation
)

import json
from .src.rag.app.ollama_interface import OllamaClient

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

    st.title("🌍 Travel Planner Assistant")

    # Language selection
    language = st.sidebar.selectbox(
        "Select Language",
        ["English", "Spanish", "French", "German", "Italian", "Portuguese"],
    )
    if "language" not in state:
        state["language"] = language
    if state["language"] != language:
        state["language"] = language
        state["conversation"] = None
        state["collected_data"] = {}
        state["chat_history"] = []

    # Selección de modelo Ollama
    ollama_client = OllamaClient()
    available_models = ollama_client.list_models()
    if not available_models:
        st.sidebar.error("No Ollama models found. Please add a model to Ollama.")
        return
    if "ollama_model" not in state or state["ollama_model"] not in available_models:
        state["ollama_model"] = available_models[0]
    selected_model = st.sidebar.selectbox(
        "Select Ollama Model",
        available_models,
        index=available_models.index(state["ollama_model"]),
        format_func=lambda x: f"🤖 {x}",
        help="Choose the local LLM model for responses.",
    )
    state["ollama_model"] = selected_model

    # Inicialización de la conversación con el modelo seleccionado
    if "conversation" not in state or state["conversation"] is None:
        state["conversation"] = initialize_conversation(state["language"], state["ollama_model"])

    if "collected_data" not in state:
        state["collected_data"] = {}
    if "chat_history" not in state:
        state["chat_history"] = []

    # Chat interface
    user_input = st.chat_input("Say something to your travel assistant...")

    if user_input:
        reply, state["conversation"], state["collected_data"] = chatbot_conversation(
            user_input,
            state["conversation"],
            state["collected_data"],
            state["language"],
            model=state["ollama_model"]
        )
        state["chat_history"].append((user_input, reply))

    # Display chat messages with chat bubbles and avatars
    for user_msg, bot_msg in state["chat_history"]:
        # User message (left-aligned)
        st.markdown(
            f"""
            <div class="chat-row chat-row-user">
                <div class="chat-avatar">🧑</div>
                <div class="chat-bubble-user">{user_msg}</div>
            </div>
            """,
            unsafe_allow_html=True
        )
        # Assistant message (right-aligned)
        st.markdown(
            f"""
            <div class="chat-row chat-row-assistant">
                <div style="flex:1"></div>
                <div class="chat-bubble-assistant">{bot_msg}</div>
                <div class="chat-avatar">🤖</div>
            </div>
            """,
            unsafe_allow_html=True
        )

    # Sidebar to show collected data in a stylized form
    st.sidebar.header("🧳 Collected Travel Data")
    if state["collected_data"]:
        for key, value in state["collected_data"].items():
            st.sidebar.text_input(
                label=key.replace("_", " ").capitalize(),
                value=str(value),
                disabled=True
            )
    else:
        st.sidebar.info("No travel data collected yet.")

    # Option to download data
    if state["collected_data"]:
        st.sidebar.download_button(
            label="Download Preferences as JSON",
            data=json.dumps(state["collected_data"], indent=2),
            file_name="travel_preferences.json",
            mime="application/json",
        )
