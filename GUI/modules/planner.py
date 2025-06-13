import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../")))
import streamlit as st
from src.data.hotel_repository import HotelRepository
from src.planner.graph_explorer import GraphExplorer
from src.planner.aco_planner import ACOPlanner  # <-- Importar ACOPlanner


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
        metodo = st.radio(
            "Método de planificación", ["Clásico (búsqueda)", "Metaheurística (ACO)"]
        )
        if metodo == "Metaheurística (ACO)":
            num_ants = st.slider("Número de hormigas", 5, 50, 15)
            num_iter = st.slider("Iteraciones", 10, 200, 50)
            alpha = st.slider("Peso estrellas (α)", 0.0, 3.0, 1.0)
            beta = st.slider("Peso costo (β)", 0.0, 3.0, 1.0)
            gamma = st.slider("Peso cambios (γ)", 0.0, 3.0, 1.0)
            evaporation = st.slider("Evaporación feromona", 0.0, 1.0, 0.5)

    if st.button("Generar itinerario"):
        # Cargar hoteles y planificar usando el planner real
        csv_path = os.path.abspath(
            os.path.join(os.path.dirname(__file__), "../../tourism_data.csv")
        )
        repo = HotelRepository.from_csv(csv_path)
        if metodo == "Clásico (búsqueda)":
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
                st.error(
                    "No se encontró un itinerario válido para los parámetros dados."
                )
        else:
            planner = ACOPlanner(
                repo,
                tiempo,
                presupuesto,
                destino,
                num_ants=num_ants,
                num_iter=num_iter,
                alpha=alpha,
                beta=beta,
                gamma=gamma,
                evaporation=evaporation,
            )
            best_solution, best_fitness = planner.search_best_path()
            if best_solution:
                state["itinerario"] = [
                    {
                        "dia": i + 1,
                        "actividad": f"Hotel: {hotel.name} ({hotel.stars}★)",
                        "costo": hotel.price,
                    }
                    for i, hotel in enumerate(best_solution)
                ]
                total_stars = sum(h.stars for h in best_solution)
                total_cost = sum(h.price for h in best_solution)
                cambios = sum(
                    1
                    for i in range(1, len(best_solution))
                    if best_solution[i] != best_solution[i - 1]
                )
                st.success(
                    f"¡Itinerario generado con ACO! Estrellas: {total_stars}, Costo: ${total_cost:.2f}, Cambios de hotel: {cambios}, Fitness: {best_fitness:.3f}"
                )
            else:
                state["itinerario"] = []
                st.error(
                    "No se encontró un itinerario válido para los parámetros dados."
                )

    # Vista previa de itinerario
    st.subheader("Itinerario Detallado")
    for item in state.get("itinerario", []):
        st.markdown(f"**Día {item['dia']}**: {item['actividad']} (${item['costo']})")
