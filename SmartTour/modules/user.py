import streamlit as st

def render(state):
    st.header("👤 Gestión de Usuario")
    st.text_input("Nombre de usuario", key="username")
    st.text_input("Correo electrónico", key="email")
    st.button("Guardar perfil")
    st.button("Cerrar sesión")
