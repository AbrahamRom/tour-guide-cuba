import streamlit as st

def get_state():
    if 'state' not in st.session_state:
        st.session_state['state'] = {
            "usuario": {},
            "historial_chat": [],
            "preferencias": {},
            "recomendaciones": [],
            "itinerario": [],
            "resultados_rag": [],
            "simulacion": {},
            "notificaciones": [],
            "idioma": "Español",
        }
    return st.session_state['state']