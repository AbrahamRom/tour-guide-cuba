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
        # --- Preferencias difusas ---
        budget_choice = st.selectbox(
            "¿Qué tan importante es ajustar el presupuesto?",
            [
                "Ahorrar lo máximo posible",
                "Ahorrar bastante",
                "Gasto equilibrado",
                "Gastar cerca del presupuesto",
                "Gastar más si es necesario",
            ],
        )
        changes_choice = st.selectbox(
            "¿Qué tan importante es evitar cambios de hotel?",
            [
                "No quiero moverme nunca",
                "Prefiero pocos cambios",
                "Indiferente",
                "Me gusta cambiar a veces",
                "Quiero probar muchos hoteles",
            ],
        )
        stars_choice = st.selectbox(
            "¿Qué tan importante es la calificación del hotel?",
            [
                "Solo los mejores hoteles",
                "Prefiero buena calidad",
                "Indiferente",
                "Me conformo con lo básico",
                "No me importa la calificación",
            ],
        )
        # Mapeo ajustado: el valor máximo es 10, el mínimo es 0
        fuzzy_map = {
            "Ahorrar lo máximo posible": 5.0,
            "Ahorrar bastante": 2.5,
            "Gasto equilibrado": 1.0,
            "Gastar cerca del presupuesto": 0.5,
            "Gastar más si es necesario": 0.1,
            "No quiero moverme nunca": 10.0,
            "Prefiero pocos cambios": 3.0,
            "Indiferente": 1.0,
            "Me gusta cambiar a veces": 0.5,
            "Quiero probar muchos hoteles": 0.1,
            "Solo los mejores hoteles": 5.0,
            "Prefiero buena calidad": 2.5,
            "Me conformo con lo básico": 0.5,
            "No me importa la calificación": 0.1,
        }
        beta = fuzzy_map[budget_choice]
        gamma = fuzzy_map[changes_choice]
        alpha = fuzzy_map[stars_choice]
        params = {}
        if metodo == "Metaheurística (ACO)":
            params["alpha"] = alpha
            params["beta"] = beta
            params["gamma"] = gamma
        elif metodo == "Metaheurística (PSO)":
            params["alpha"] = alpha
            params["beta"] = beta
            params["gamma"] = gamma
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
        return (
            [],
            "No se encontró un itinerario válido para los parámetros dados.",
            "error",
        )


def planificar_aco(repo, tiempo, presupuesto, destino, params):
    planner = ACOPlanner(
        repo,
        tiempo,
        presupuesto,
        destino,
        alpha=params["alpha"],
        beta=params["beta"],
        gamma=params["gamma"],
    )
    best_solution, best_fitness = planner.search_best_path()
    if best_solution:
        total_stars = sum(h.stars for h in best_solution)
        total_cost = sum(h.price for h in best_solution)
        cambios = sum(
            1
            for i in range(1, len(best_solution))
            if best_solution[i] != best_solution[i - 1]
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
        return (
            [],
            "No se encontró un itinerario válido para los parámetros dados.",
            "error",
        )


def planificar_pso(repo, tiempo, presupuesto, destino, params):
    planner = PSOPlanner(
        repo,
        tiempo,
        presupuesto,
        destino,
        alpha=params["alpha"],
        beta=params["beta"],
        gamma=params["gamma"],
    )
    best_solution, best_fitness = planner.search_best_path()
    if best_solution:
        total_stars = sum(h.stars for h in best_solution)
        total_cost = sum(h.price for h in best_solution)
        cambios = sum(
            1
            for i in range(1, len(best_solution))
            if best_solution[i] != best_solution[i - 1]
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
        return (
            [],
            "No se encontró un itinerario válido para los parámetros dados.",
            "error",
        )


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
            itinerario, mensaje, tipo = planificar_clasico(
                repo, tiempo, presupuesto, destino
            )
        elif metodo == "Metaheurística (ACO)":
            itinerario, mensaje, tipo = planificar_aco(
                repo, tiempo, presupuesto, destino, params
            )
        elif metodo == "Metaheurística (PSO)":
            itinerario, mensaje, tipo = planificar_pso(
                repo, tiempo, presupuesto, destino, params
            )
        state["itinerario"] = itinerario
        if tipo == "success":
            st.success(mensaje)
        else:
            st.error(mensaje)

    mostrar_itinerario(state.get("itinerario", []))
