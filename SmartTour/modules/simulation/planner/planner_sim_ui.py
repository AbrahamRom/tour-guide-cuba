# simulator/planner_sim_ui.py
import streamlit as st
from .planner_sim import run_planner

methods = ["Clásico (búsqueda)", "Metaheurística (ACO)", "Metaheurística (PSO)"]


def render_planner_simulator():
    st.title("🧠 Planner Simulation")

    tiempo = st.slider("Tiempo (días)", 1, 14, 5)
    presupuesto = st.slider("Presupuesto ($USD)", 100, 3000, 1000)
    destino = st.text_input("Destino", "La Habana")
    dataset_path = st.text_input("Ruta CSV de hoteles", "DATA/tourism_data.csv")

    alpha = st.slider("Importancia calidad hotel", 0.1, 5.0, 2.5)
    beta = st.slider("Importancia presupuesto", 0.1, 5.0, 1.0)
    gamma = st.slider("Importancia cambios de hotel", 0.1, 5.0, 1.0)

    params = {"alpha": alpha, "beta": beta, "gamma": gamma}

    if st.button("▶️ Ejecutar simulación"):
        for method in methods:
            result = run_planner(method, tiempo, presupuesto, destino, params, dataset_path)
            if "error" in result:
                st.error(f"{method}: {result['error']}")
            else:
                st.success(f"{result['method']} completado en {result['latency']}s")
                st.write(f"⭐ Estrellas: {result['stars']}  | 💵 Costo: ${result['cost']:.2f}  | 🔁 Cambios: {result['changes']}")
                if result.get("fitness") is not None:
                    st.write(f"📈 Fitness: {result['fitness']}")