import sys
import os
import streamlit as st

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../")))
from src.data.hotel_repository import HotelRepository
from src.planner.graph_explorer import GraphExplorer
from src.planner.aco_planner import ACOPlanner
from src.planner.pso_planner import PSOPlanner


def get_configuracion():
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
            "Método de planificación",
            ["Clásico (búsqueda)", "Metaheurística (ACO)", "Metaheurística (PSO)"],
        )
        params = {}
        if metodo == "Metaheurística (ACO)":
            params["num_ants"] = st.slider("Número de hormigas", 5, 50, 15)
            params["num_iter"] = st.slider("Iteraciones", 10, 200, 50)
            params["alpha"] = st.slider("Peso estrellas (α)", 0.0, 3.0, 1.0)
            params["beta"] = st.slider("Peso costo (β)", 0.0, 3.0, 1.0)
            params["gamma"] = st.slider("Peso cambios (γ)", 0.0, 3.0, 1.0)
            params["evaporation"] = st.slider("Evaporación feromona", 0.0, 1.0, 0.5)
        elif metodo == "Metaheurística (PSO)":
            params["num_particles"] = st.slider("Número de partículas", 5, 50, 20)
            params["num_iter"] = st.slider("Iteraciones", 10, 200, 50)
            params["alpha"] = st.slider("Peso estrellas (α)", 0.0, 3.0, 1.0)
            params["beta"] = st.slider("Peso costo (β)", 0.0, 3.0, 1.0)
            params["gamma"] = st.slider("Peso cambios (γ)", 0.0, 3.0, 1.0)
        return tiempo, presupuesto, destino, prioridad, metodo, params


def planificar_clasico(repo, tiempo, presupuesto, destino):
    explorer = GraphExplorer(repo, tiempo, presupuesto, destino)
    best_node = explorer.search_best_path()
    if best_node:
        return (
            [
                {
                    "dia": night,
                    "actividad": f"Hotel: {hotel.name} ({hotel.stars}★)",
                    "costo": hotel.price,
                }
                for night, hotel in best_node.path
            ],
            f"¡Itinerario generado! Total estrellas: {best_node.stars_accum}. Presupuesto restante: ${best_node.budget_left:.2f}",
            "success",
        )
    else:
        return [], "No se encontró un itinerario válido para los parámetros dados.", "error"


def planificar_aco(repo, tiempo, presupuesto, destino, params):
    planner = ACOPlanner(
        repo,
        tiempo,
        presupuesto,
        destino,
        num_ants=params["num_ants"],
        num_iter=params["num_iter"],
        alpha=params["alpha"],
        beta=params["beta"],
        gamma=params["gamma"],
        evaporation=params["evaporation"],
    )
    best_solution, best_fitness = planner.search_best_path()
    if best_solution:
        total_stars = sum(h.stars for h in best_solution)
        total_cost = sum(h.price for h in best_solution)
        cambios = sum(
            1 for i in range(1, len(best_solution)) if best_solution[i] != best_solution[i - 1]
        )
        return (
            [
                {
                    "dia": i + 1,
                    "actividad": f"Hotel: {hotel.name} ({hotel.stars}★)",
                    "costo": hotel.price,
                }
                for i, hotel in enumerate(best_solution)
            ],
            f"¡Itinerario generado con ACO! Estrellas: {total_stars}, Costo: ${total_cost:.2f}, Cambios de hotel: {cambios}, Fitness: {best_fitness:.3f}",
            "success",
        )
    else:
        return [], "No se encontró un itinerario válido para los parámetros dados.", "error"


def planificar_pso(repo, tiempo, presupuesto, destino, params):
    planner = PSOPlanner(
        repo,
        tiempo,
        presupuesto,
        destino,
        num_particles=params["num_particles"],
        num_iter=params["num_iter"],
        alpha=params["alpha"],
        beta=params["beta"],
        gamma=params["gamma"],
    )
    best_solution, best_fitness = planner.search_best_path()
    if best_solution:
        total_stars = sum(h.stars for h in best_solution)
        total_cost = sum(h.price for h in best_solution)
        cambios = sum(
            1 for i in range(1, len(best_solution)) if best_solution[i] != best_solution[i - 1]
        )
        return (
            [
                {
                    "dia": i + 1,
                    "actividad": f"Hotel: {hotel.name} ({hotel.stars}★)",
                    "costo": hotel.price,
                }
                for i, hotel in enumerate(best_solution)
            ],
            f"¡Itinerario generado con PSO! Estrellas: {total_stars}, Costo: ${total_cost:.2f}, Cambios de hotel: {cambios}, Fitness: {best_fitness:.3f}",
            "success",
        )
    else:
        return [], "No se encontró un itinerario válido para los parámetros dados.", "error"


def mostrar_itinerario(itinerario):
    st.subheader("Itinerario Detallado")
    for item in itinerario:
        st.markdown(f"**Día {item['dia']}**: {item['actividad']} (${item['costo']})")


def render(state):
    st.header("🗺️ Planificador de Rutas")
    st.markdown("Visualiza y ajusta tu itinerario de viaje.")
    tiempo, presupuesto, destino, prioridad, metodo, params = get_configuracion()

    if st.button("Generar itinerario"):
        csv_path = os.path.abspath(
            os.path.join(os.path.dirname(__file__), "../../tourism_data.csv")
        )
        repo = HotelRepository.from_csv(csv_path)
        if metodo == "Clásico (búsqueda)":
            itinerario, mensaje, tipo = planificar_clasico(repo, tiempo, presupuesto, destino)
        elif metodo == "Metaheurística (ACO)":
            itinerario, mensaje, tipo = planificar_aco(repo, tiempo, presupuesto, destino, params)
        elif metodo == "Metaheurística (PSO)":
            itinerario, mensaje, tipo = planificar_pso(repo, tiempo, presupuesto, destino, params)
        state["itinerario"] = itinerario
        if tipo == "success":
            st.success(mensaje)
        else:
            st.error(mensaje)

    mostrar_itinerario(state.get("itinerario", []))
