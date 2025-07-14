import sys
import os
import streamlit as st

# --- Importación de módulos del proyecto ---
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../")))
from .src.data.hotel_repository import HotelRepository
from .src.planner.graph_explorer import GraphExplorer
from .src.planner.aco_planner import ACOPlanner
from .src.planner.pso_planner import PSOPlanner
from . import map  # Importa el módulo del mapa

# --- Mapeo difuso para preferencias del usuario ---
FUZZY_MAP = {
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


# --- Configuración de restricciones y preferencias del usuario ---
# --- Configuración global para el directorio de destinos ---

DESTINATIONS_DIR = os.path.join(os.path.dirname(__file__), "../../DATA/destinations/")


def get_configuracion(tiempo, presupuesto):
    """
    Muestra los controles de configuración y preferencias difusas para el usuario.
    Devuelve los parámetros seleccionados y los pesos difusos para el planificador.
    """
    with st.expander("Configuración de restricciones"):
        # Los sliders de tiempo y presupuesto han sido eliminados
        st.info(f"Duración del viaje: {tiempo} días | Presupuesto: ${presupuesto}")

        # Obtener destinos disponibles dinámicamente
        try:
            from .src.data.split_tourism_data import get_available_destinations

            available_destinations = get_available_destinations(DESTINATIONS_DIR)
            if not available_destinations:
                available_destinations = [
                    "La Habana",
                    "Varadero",
                    "Santiago",
                ]  # Fallback
        except Exception as e:
            st.warning(f"Error cargando destinos: {e}")
            available_destinations = ["La Habana", "Varadero", "Santiago"]  # Fallback

        destino = st.selectbox("Destino", available_destinations)
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
        # Preferencias difusas
        budget_choice = st.selectbox(
            "¿Qué tan importante es ajustar el presupuesto?",
            list(FUZZY_MAP.keys())[:5],
        )
        changes_choice = st.selectbox(
            "¿Qué tan importante es evitar cambios de hotel?",
            list(FUZZY_MAP.keys())[5:10],
        )
        stars_choice = st.selectbox(
            "¿Qué tan importante es la calificación del hotel?",
            list(FUZZY_MAP.keys())[10:],
        )
        # Traducción de preferencias a pesos
        beta = FUZZY_MAP[budget_choice]
        gamma = FUZZY_MAP[changes_choice]
        alpha = FUZZY_MAP[stars_choice]
        params = {"alpha": alpha, "beta": beta, "gamma": gamma}
        return destino, prioridad, metodo, params


# --- Planificación clásica ---
def planificar_clasico(tiempo, presupuesto, destino, params):
    """
    Ejecuta la planificación clásica (búsqueda) y retorna el itinerario y mensaje.
    """
    # Usar el nuevo sistema de carga por destino
    try:
        repo = HotelRepository.from_single_destination(destino, DESTINATIONS_DIR)
    except FileNotFoundError as e:
        return [], f"Error: {e}", "error"

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


# --- Planificación con ACO ---
def planificar_aco(tiempo, presupuesto, destino, params):
    """
    Ejecuta la planificación con ACO y retorna el itinerario y mensaje.
    """
    # Usar el nuevo sistema de carga por destino
    try:
        repo = HotelRepository.from_single_destination(destino, DESTINATIONS_DIR)
    except FileNotFoundError as e:
        return [], f"Error: {e}", "error"

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


# --- Planificación con PSO ---
def planificar_pso(tiempo, presupuesto, destino, params):
    """
    Ejecuta la planificación con PSO y retorna el itinerario y mensaje.
    """
    # Usar el nuevo sistema de carga por destino
    try:
        repo = HotelRepository.from_single_destination(destino, DESTINATIONS_DIR)
    except FileNotFoundError as e:
        return [], f"Error: {e}", "error"

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


def itinerario_a_ubicaciones(itinerario):
    """
    Convierte el itinerario en una lista de ubicaciones para el mapa, organizadas por días.
    Cada ubicación es un dict con 'name' y 'popup' (día y actividad).
    Asume que todos los hoteles están ubicados en Cuba.
    """
    ubicaciones = []
    for item in itinerario:
        # Extrae el nombre del hotel y asegura que termine con ', Cuba'
        nombre_hotel = item["actividad"].split(":")[-1].strip()
        if not nombre_hotel.endswith("Cuba"):
            nombre_hotel = f"{nombre_hotel}, Cuba"
        ubicaciones.append(
            {
                "name": nombre_hotel,
                "popup": f"Día {item['dia']}: {item['actividad']} (${item['costo']})",
            }
        )
    return ubicaciones


# --- Mostrar itinerario detallado ---
def mostrar_itinerario(itinerario):
    """
    Muestra el itinerario detallado en la interfaz y el botón para ver el mapa.
    """
    st.subheader("Itinerario Detallado")
    for item in itinerario:
        st.markdown(f"**Día {item['dia']}**: {item['actividad']} (${item['costo']})")
    if itinerario:
        col1, col2 = st.columns([3, 1])
        with col2:
            if st.button("🗺️ Ver mapa", help="Visualiza el itinerario en el mapa"):
                st.session_state["mostrar_mapa"] = True
        # Mostrar el mapa si la bandera está activa
        if st.session_state.get("mostrar_mapa", False):
            ubicaciones = itinerario_a_ubicaciones(itinerario)
            map.itinerary_map_view(ubicaciones, title="Mapa del Itinerario por Días")


# --- Render principal del módulo de planificación ---
def render(state):
    """
    Renderiza la interfaz del planificador de rutas y gestiona la generación del itinerario.
    """
    st.header("🗺️ Planificador de Rutas")
    st.markdown("Visualiza y ajusta tu itinerario de viaje.")
    # --- Extraer budget y travel_duration desde state["collected_data"] o usar valores por defecto ---
    collected = state.get("collected_data", {})
    try:
        presupuesto = float(collected.get("budget", 1000))
    except Exception:
        presupuesto = 1000
    try:
        tiempo = int(collected.get("travel_duration", 7))
    except Exception:
        tiempo = 7
    # Obtener configuración de preferencias difusas y otros parámetros
    destino, prioridad, metodo, params = get_configuracion(tiempo, presupuesto)
    st.info(f"Duración del viaje: {tiempo} días | Presupuesto: ${presupuesto}")

    if st.button("Generar itinerario"):
        if metodo == "Clásico (búsqueda)":
            itinerario, mensaje, tipo = planificar_clasico(
                tiempo, presupuesto, destino, params
            )
        elif metodo == "Metaheurística (ACO)":
            itinerario, mensaje, tipo = planificar_aco(
                tiempo, presupuesto, destino, params
            )
        elif metodo == "Metaheurística (PSO)":
            itinerario, mensaje, tipo = planificar_pso(
                tiempo, presupuesto, destino, params
            )
        state["itinerario"] = itinerario
        # Oculta el mapa al generar un nuevo itinerario
        st.session_state["mostrar_mapa"] = False
        if tipo == "success":
            st.success(mensaje)
        else:
            st.error(mensaje)

    mostrar_itinerario(state.get("itinerario", []))
