import streamlit as st

def render(state):
    st.header("🗺️ Planificador de Rutas")
    st.markdown("Visualiza y ajusta tu itinerario de viaje.")

    # Configuración de restricciones
    with st.expander("Configuración de restricciones"):
        tiempo = st.slider("Tiempo máximo (días)", 1, 30, 7)
        presupuesto = st.slider("Presupuesto máximo ($USD)", 100, 5000, 1000)
        prioridad = st.selectbox("Prioridad", ["Evitar transporte costoso", "Maximizar actividades", "Minimizar traslados"])

    # Editor de itinerario
    if st.button("Generar itinerario"):
        # ... lógica de planificación ...
        state["itinerario"] = [
            {"dia": 1, "actividad": "Tour por La Habana", "costo": 50},
            {"dia": 2, "actividad": "Playa en Varadero", "costo": 100},
        ]

    # Mapa interactivo (placeholder)
    st.map()  # Reemplazar con mapa real

    # Vista previa de itinerario
    st.subheader("Itinerario Detallado")
    for item in state.get("itinerario", []):
        st.markdown(f"**Día {item['dia']}**: {item['actividad']} (${item['costo']})")
