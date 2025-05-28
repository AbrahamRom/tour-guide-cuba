import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../")))
import streamlit as st
from src.data.hotel_repository import HotelRepository
from src.planner.graph_explorer import GraphExplorer


def render(state):
    st.header("🗺️ Planificador de Rutas")
    st.markdown("Visualiza y ajusta tu itinerario de viaje.")

    # Configuración de restricciones
    with st.expander("Configuración de restricciones"):
        tiempo = st.slider("Tiempo máximo (días)", 1, 30, 7)
        presupuesto = st.slider("Presupuesto máximo ($USD)", 50, 5000, 1000)
        destino = st.text_input("Destino", "La Habana")
        prioridad = st.selectbox(
            "Prioridad",
            [
                "Maximizar estrellas de hotel",
                "Evitar transporte costoso",
                "Maximizar actividades",
                "Minimizar traslados",
            ],
        )

    if st.button("Generar itinerario"):
        # Cargar hoteles y planificar usando el planner real
        csv_path = os.path.abspath(
            os.path.join(os.path.dirname(__file__), "../../tourism_data.csv")
        )
        repo = HotelRepository.from_csv(csv_path)
        explorer = GraphExplorer(repo, tiempo, presupuesto, destino)
        best_node = explorer.search_best_path()
        if best_node:
            state["itinerario"] = [
                {
                    "dia": night,
                    "actividad": f"Hotel: {hotel.name} ({hotel.stars}★)",
                    "costo": hotel.price,
                }
                for night, hotel in best_node.path
            ]
            st.success(
                f"¡Itinerario generado! Total estrellas: {best_node.stars_accum}. Presupuesto restante: ${best_node.budget_left:.2f}"
            )
        else:
            state["itinerario"] = []
            st.error("No se encontró un itinerario válido para los parámetros dados.")

    # Mapa interactivo (placeholder)
    st.map()  # Reemplazar con mapa real

    # Vista previa de itinerario
    st.subheader("Itinerario Detallado")
    for item in state.get("itinerario", []):
        st.markdown(f"**Día {item['dia']}**: {item['actividad']} (${item['costo']})")
