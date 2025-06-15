import streamlit as st
import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))
from state import get_state
from modules import (
    chatbot,
    recommender,
    planner,
    rag,
    simulator,
    knowledge,
    user,
    export,
    notifications,
    help,
)

st.set_page_config(page_title="SmartTour Cuba", layout="wide", page_icon=":palm_tree:")

# Custom CSS for modern look and animated menu
css_path = os.path.join(os.path.dirname(__file__), "assets", "style.css")
with open(css_path) as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

st.markdown(
    """
    <style>
    .menu-btn {
        border-radius: 20px;
        background: linear-gradient(90deg, #00b894 0%, #00cec9 100%);
        color: white;
        font-size: 1.2em;
        font-weight: bold;
        padding: 1.2em 1.5em;
        margin: 0.5em;
        border: none;
        box-shadow: 0 2px 8px #0002;
        transition: transform 0.15s, box-shadow 0.15s, background 0.2s;
    }
    .menu-btn:hover {
        background: linear-gradient(90deg, #00cec9 0%, #00b894 100%);
        transform: scale(1.07) rotate(-2deg);
        box-shadow: 0 6px 24px #00b89444;
        cursor: pointer;
    }
    .main-logo {
        display: block;
        margin-left: auto;
        margin-right: auto;
        width: 220px;
        margin-bottom: 1.5em;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

menu_items = [
    ("Chatbot", "💬"),
    ("Recomendador", "✨"),
    ("Planificador de Rutas", "🗺️"),
    ("Recuperador", "🔎"),
    ("Simulador", "🎲"),
    ("Base de Conocimiento", "📚"),
    ("Gestión de Usuario", "👤"),
    ("Exportar/Compartir", "📤"),
    ("Notificaciones", "🔔"),
    ("Ayuda", "❓"),
]

menu_keys = [label for label, icon in menu_items]

if "menu" not in st.session_state:
    st.session_state.menu = "Inicio"


# --- Manejo del botón Inicio ---
def go_home():
    st.session_state.menu = "Inicio"


# Página principal (Inicio)
if st.session_state.menu == "Inicio":
    logo_path = os.path.join(os.path.dirname(__file__), "assets", "logo.png")
    st.image(logo_path, use_container_width=False, output_format="PNG", width=140)
    st.markdown(
        "<h1 style='text-align:center; color:#00b894;'>SmartTour Cuba</h1>",
        unsafe_allow_html=True,
    )
    st.markdown(
        "<h4 style='text-align:center; color:#636e72;'>Tu asistente inteligente de viajes en Cuba</h4>",
        unsafe_allow_html=True,
    )
    st.write("")
    # Menú animado en grid
    cols = st.columns(2)
    for i in range(0, len(menu_items), 2):
        with cols[0]:
            if st.button(
                f"{menu_items[i][1]}  {menu_items[i][0]}",
                key=f"menu_{menu_items[i][0]}",
                help=menu_items[i][0],
                use_container_width=True,
            ):
                st.session_state.menu = menu_items[i][0]
                st.rerun()
        if i + 1 < len(menu_items):
            with cols[1]:
                if st.button(
                    f"{menu_items[i+1][1]}  {menu_items[i+1][0]}",
                    key=f"menu_{menu_items[i+1][0]}",
                    help=menu_items[i + 1][0],
                    use_container_width=True,
                ):
                    st.session_state.menu = menu_items[i + 1][0]
                    st.rerun()
    st.write("")
    st.markdown(
        "<div style='text-align:center; color:#636e72;'>Selecciona una opción para comenzar</div>",
        unsafe_allow_html=True,
    )
else:
    # Botón para volver al inicio (funcional)
    col_home, col_spacer = st.columns([1, 9])
    with col_home:
        if st.button(
            "🏠 Inicio",
            key="btn_inicio",
            help="Volver al inicio",
            use_container_width=True,
        ):
            go_home()
            st.rerun()

    state = get_state()
    menu = st.session_state.menu
    if menu == "Chatbot":
        chatbot.render(state)
    elif menu == "Recomendador":
        recommender.render(state)
    elif menu == "Planificador de Rutas":
        planner.render(state)
    elif menu == "Recuperador":
        rag.render(state)
    elif menu == "Simulador":
        simulator.render(state)
    elif menu == "Base de Conocimiento":
        knowledge.render(state)
    elif menu == "Gestión de Usuario":
        user.render(state)
    elif menu == "Exportar/Compartir":
        export.render(state)
    elif menu == "Notificaciones":
        notifications.render(state)
    elif menu == "Ayuda":
        help.render(state)
