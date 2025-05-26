import streamlit as st

def render(state):
    st.header("🤖 Asistente Virtual")
    st.markdown("Interactúa con el asistente para planificar tu viaje por Cuba.")

    # Selector de idioma
    idioma = st.selectbox("Selecciona el idioma", ["Español", "Inglés", "Francés"], key="idioma")
    state["idioma"] = idioma

    # Preguntas frecuentes
    with st.expander("Preguntas Frecuentes"):
        st.markdown("- ¿Cuáles son los mejores lugares para visitar en Cuba?")
        st.markdown("- ¿Cómo es el clima en julio?")
        st.markdown("- ¿Qué actividades culturales hay en La Habana?")

    # Chat interactivo
    chat_input = st.text_input("Escribe tu mensaje:", key="chat_input")
    if chat_input:
        # ... lógica de chatbot ...
        state["historial_chat"].append({"usuario": chat_input, "bot": "Respuesta del asistente..."})

    # Historial de conversación
    st.subheader("Historial de Conversación")
    for msg in state["historial_chat"]:
        st.markdown(f"**Tú:** {msg['usuario']}")
        st.markdown(f"**Asistente:** {msg['bot']}")
