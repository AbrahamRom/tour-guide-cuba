import streamlit as st

def render(state):
    st.header("🌀 Simulador de Escenarios")
    st.markdown("Simula condiciones hipotéticas y observa los cambios en tu itinerario.")

    clima = st.selectbox("Escenario climático", ["Soleado", "Lluvia", "Tormenta"])
    evento = st.text_input("Evento especial (opcional):")

    if st.button("Simular"):
        # ... lógica de simulación ...
        state["simulacion"] = {
            "original": state.get("itinerario", []),
            "ajustado": [{"dia": 1, "actividad": "Museo Nacional (bajo techo)", "costo": 30}]
        }
        st.toast("¡Itinerario ajustado por contingencia!", icon="⚠️")

    if state.get("simulacion"):
        st.subheader("Comparación de Itinerarios")
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("**Original**")
            for item in state["simulacion"].get("original", []):
                st.markdown(f"{item}")
        with col2:
            st.markdown("**Ajustado**")
            for item in state["simulacion"].get("ajustado", []):
                st.markdown(f"{item}")
