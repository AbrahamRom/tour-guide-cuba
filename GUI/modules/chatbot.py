import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../")))

import streamlit as st

from .bot import (
    initialize_conversation,
    chatbot_conversation
)

import json


def render(state):
    # Set Streamlit page config
    # st.set_page_config(page_title="Travel Planner Chatbot", layout="wide")

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
        state["conversation"] = initialize_conversation(language)
        state["collected_data"] = {}
        state["chat_history"] = []

    # Session state initialization (use dict keys, not attributes)
    if "conversation" not in state:
        state["conversation"] = initialize_conversation(state["language"])
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
            state["language"]

        )
        state["chat_history"].append((user_input, reply))

    # Display chat messages with alignment
    for user_msg, bot_msg in state["chat_history"]:
        # User message (left-aligned)
        with st.chat_message("user"):
            st.markdown(
                f"""
                <div style='text-align: left;'>
                    {user_msg}
                </div>
                """,
                unsafe_allow_html=True
            )
        # Assistant message (right-aligned)
        with st.chat_message("assistant"):
            st.markdown(
                f"""
                <div style='text-align: right;'>
                    {bot_msg}
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
