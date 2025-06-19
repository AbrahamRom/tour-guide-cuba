import streamlit as st

def render(state):
    st.header("🔔 Notificaciones")
    for notif in state.get("notificaciones", []):
        st.toast(notif, icon="🔔")
    st.info("Aquí aparecerán alertas sobre cambios en clima, eventos o lugares.")
