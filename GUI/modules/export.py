import streamlit as st

def render(state):
    st.header("📤 Exportar / Compartir")
    st.button("Descargar itinerario (PDF)")
    st.button("Descargar itinerario (Excel)")
    st.button("Compartir por correo")
    st.button("Compartir en redes sociales")
