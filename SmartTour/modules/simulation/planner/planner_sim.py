# simulator/planner_sim.py
import time
from modules.src.data.hotel_repository import HotelRepository
from modules.src.planner.aco_planner import ACOPlanner
from modules.src.planner.pso_planner import PSOPlanner
from modules.src.planner.graph_explorer import GraphExplorer


def run_planner(method, tiempo, presupuesto, destino, params, destinations_dir):
    """Actualizado para usar directorio de destinos"""
    try:
        repo = HotelRepository.from_single_destination(destino, destinations_dir)
    except FileNotFoundError:
        # Fallback a directorio completo si no encuentra el destino específico
        repo = HotelRepository.from_destinations_directory(destinations_dir)

    start = time.time()
    if method == "Clásico (búsqueda)":
        explorer = GraphExplorer(repo, tiempo, presupuesto, destino)
        best_node = explorer.search_best_path()
        end = time.time()
        if best_node:
            total_cost = sum(h.price for _, h in best_node.path)
            total_stars = best_node.stars_accum
            cambios = sum(
                1
                for i in range(1, len(best_node.path))
                if best_node.path[i][1] != best_node.path[i - 1][1]
            )
            return {
                "method": method,
                "latency": round(end - start, 2),
                "stars": total_stars,
                "cost": total_cost,
                "changes": cambios,
                "fitness": None,
            }
    elif method == "Metaheurística (ACO)":
        planner = ACOPlanner(repo, tiempo, presupuesto, destino, **params)
        solution, fitness = planner.search_best_path()
        end = time.time()
        if solution:
            total_stars = sum(h.stars for h in solution)
            total_cost = sum(h.price for h in solution)
            cambios = sum(
                1 for i in range(1, len(solution)) if solution[i] != solution[i - 1]
            )
            return {
                "method": method,
                "latency": round(end - start, 2),
                "stars": total_stars,
                "cost": total_cost,
                "changes": cambios,
                "fitness": round(fitness, 3),
            }
    elif method == "Metaheurística (PSO)":
        planner = PSOPlanner(repo, tiempo, presupuesto, destino, **params)
        solution, fitness = planner.search_best_path()
        end = time.time()
        if solution:
            total_stars = sum(h.stars for h in solution)
            total_cost = sum(h.price for h in solution)
            cambios = sum(
                1 for i in range(1, len(solution)) if solution[i] != solution[i - 1]
            )
            return {
                "method": method,
                "latency": round(end - start, 2),
                "stars": total_stars,
                "cost": total_cost,
                "changes": cambios,
                "fitness": round(fitness, 3),
            }
    return {"method": method, "latency": None, "error": "No solution found"}
