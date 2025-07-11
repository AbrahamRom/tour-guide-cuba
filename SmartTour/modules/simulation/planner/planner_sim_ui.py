# simulator/planner_sim_ui.py
import streamlit as st
from .planner_sim import run_planner
import json

methods = ["Clásico (búsqueda)", "Metaheurística (ACO)", "Metaheurística (PSO)"]


def render_planner_simulator():
    st.title("🧠 Planner Simulation")

    tiempo = st.slider("Tiempo (días)", 1, 14, 5)
    presupuesto = st.slider("Presupuesto ($USD)", 100, 3000, 1000)
    destino = st.text_input("Destino", "La Habana")
    dataset_path = st.text_input("Ruta CSV de hoteles", "../DATA/tourism_data.csv")

    alpha = st.slider("Importancia calidad hotel", 0.1, 5.0, 2.5)
    beta = st.slider("Importancia presupuesto", 0.1, 5.0, 1.0)
    gamma = st.slider("Importancia cambios de hotel", 0.1, 5.0, 1.0)

    params = {"alpha": alpha, "beta": beta, "gamma": gamma}

    if st.button("▶️ Ejecutar simulación"):
        all_results = []
        num_success = 0
        total_latency = 0
        total_stars = 0
        total_cost = 0
        total_changes = 0
        total_fitness = 0
        fitness_count = 0

        best_fitness = None
        worst_fitness = None

        for method in methods:
            result = run_planner(method, tiempo, presupuesto, destino, params, dataset_path)
            all_results.append(result)
            if "error" in result:
                st.error(f"{method}: {result['error']}")
            else:
                num_success += 1
                total_latency += result["latency"] if result["latency"] is not None else 0
                total_stars += result["stars"]
                total_cost += result["cost"]
                total_changes += result["changes"]
                if result.get("fitness") is not None:
                    total_fitness += result["fitness"]
                    fitness_count += 1
                    if best_fitness is None or result["fitness"] > best_fitness:
                        best_fitness = result["fitness"]
                    if worst_fitness is None or result["fitness"] < worst_fitness:
                        worst_fitness = result["fitness"]

                st.success(f"{result['method']} completado en {result['latency']}s")
                st.write(f"⭐ Estrellas: {result['stars']}  | 💵 Costo: ${result['cost']:.2f}  | 🔁 Cambios: {result['changes']}")
                if result.get("fitness") is not None:
                    st.write(f"📈 Fitness: {result['fitness']}")

        if num_success > 0:
            avg_latency = total_latency / num_success
            # Ajuste: promedio de estrellas por día, entre 1 y 5
            avg_stars = total_stars / (tiempo * num_success)
            avg_cost = total_cost / num_success
            avg_changes = total_changes / num_success
            avg_fitness = total_fitness / fitness_count if fitness_count else 0

            st.info(f"✅ Métodos exitosos: {num_success} / {len(methods)}")
            st.metric("Promedio Latencia (s)", f"{avg_latency:.2f}")
            st.metric("Promedio Estrellas", f"{avg_stars:.2f}")
            st.metric("Promedio Costo ($)", f"{avg_cost:.2f}")
            st.metric("Promedio Cambios de hotel", f"{avg_changes:.2f}")
            if fitness_count:
                st.metric("Promedio Fitness", f"{avg_fitness:.3f}")
                st.metric("Mejor Fitness", f"{best_fitness:.3f}")
                st.metric("Peor Fitness", f"{worst_fitness:.3f}")

            # Descargar resultados
            json_data = json.dumps(all_results, indent=2, ensure_ascii=False)
            st.download_button(
                label="📥 Descargar resultados completos (JSON)",
                data=json_data,
                file_name="planner_simulation_results.json",
                mime="application/json"
            )
        else:
            st.warning("No se obtuvo ningún resultado exitoso.")