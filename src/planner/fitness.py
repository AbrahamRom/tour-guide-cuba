from typing import List
from src.data.hotel import Hotel


def calcular_fitness(
    solution: List[Hotel],
    max_hotel_stars: int,
    budget: float,
    alpha=1.0,
    beta=1.0,
    gamma=1.0,
) -> float:
    """
    Calcula el fitness normalizado de una solución (lista de hoteles).
    Maximiza estrellas, minimiza costo y cambios de hotel.
    Penaliza fuertemente si el costo excede el presupuesto.
    """
    if not solution:
        return float("-inf")
    total_stars = sum(hotel.stars for hotel in solution)
    total_cost = sum(hotel.price for hotel in solution)
    changes = sum(1 for i in range(1, len(solution)) if solution[i] != solution[i - 1])

    # Normalización
    stars_norm = (
        total_stars / (len(solution) * max_hotel_stars) if max_hotel_stars > 0 else 0
    )
    cost_norm = min(total_cost / budget, 1) if budget > 0 else 1
    changes_norm = changes / (len(solution) - 1) if len(solution) > 1 else 0

    # Suma ponderada normalizada (todos los términos en [0,1])
    fitness = alpha * stars_norm + beta * (1 - cost_norm) + gamma * (1 - changes_norm)
    return fitness
