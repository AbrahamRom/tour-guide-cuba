from typing import List, Tuple
import random
from ..data.hotel import Hotel
from ..data.hotel_repository import HotelRepository
from .fitness import calcular_fitness


class ACOPlanner:
    """
    Planificador basado en Ant Colony Optimization (ACO) para itinerarios de hoteles.
    """

    def __init__(
        self,
        hotel_repo: HotelRepository,
        nights: int,
        budget: float,
        destino: str,
        num_ants: int = 48,  # Valor óptimo ajustado
        num_iter: int = 300,
        alpha: float = 1.0,
        beta: float = 1.0,
        gamma: float = 1.0,
        evaporation: float = 0.12,  # Valor óptimo ajustado
    ):
        """
        Inicializa el planificador ACO con los parámetros dados.
        """
        self.hotel_repo = hotel_repo
        self.nights = nights
        self.budget = budget
        self.destino = destino
        self.num_ants = num_ants
        self.num_iter = num_iter
        self.alpha = alpha
        self.beta = beta
        self.gamma = gamma
        self.evaporation = evaporation
        self.hotels = self.hotel_repo.get_hotels_by_destino(destino)
        self.max_hotel_stars = max((h.stars for h in self.hotels), default=1)
        # Inicializar feromonas: matriz [noche][hotel]
        self.pheromones = [[1.0 for _ in self.hotels] for _ in range(nights)]

    def construct_solution(self) -> List[Hotel]:
        """
        Construye una solución (itinerario) para una hormiga, respetando el presupuesto.
        """
        solution = []
        budget_left = self.budget
        last_hotel_idx = None
        for night in range(self.nights):
            probabilities = self._calculate_probabilities(
                night, budget_left, last_hotel_idx
            )
            if not probabilities:
                break
            hotel_idx = self._roulette_wheel_selection(probabilities)
            hotel = self.hotels[hotel_idx]
            if hotel.price > budget_left:
                break
            solution.append(hotel)
            budget_left -= hotel.price
            last_hotel_idx = hotel_idx
        return solution

    def _calculate_probabilities(
        self, night: int, budget_left: float, last_hotel_idx: int
    ) -> List[float]:
        """
        Calcula las probabilidades de elegir cada hotel para una noche dada.
        """
        probabilities = []
        for idx, hotel in enumerate(self.hotels):
            if hotel.price > budget_left:
                probabilities.append(0)
                continue
            pheromone = self.pheromones[night][idx]
            heuristic = hotel.stars / hotel.price if hotel.price > 0 else 0
            if last_hotel_idx is not None and idx != last_hotel_idx:
                heuristic *= 0.8  # Penaliza cambio de hotel
            probabilities.append(pheromone * heuristic)
        total = sum(probabilities)
        if total == 0:
            return []
        return [p / total for p in probabilities]

    def _roulette_wheel_selection(self, probabilities: List[float]) -> int:
        """
        Selecciona un índice basado en las probabilidades (ruleta).
        """
        r = random.random()
        cumulative = 0
        for idx, p in enumerate(probabilities):
            cumulative += p
            if r <= cumulative:
                return idx
        return len(probabilities) - 1

    def update_pheromones(self, solutions: List[List[Hotel]], fitnesses: List[float]):
        """
        Actualiza la matriz de feromonas aplicando evaporación y depósito según fitness.
        """
        # Evaporación
        for night in range(self.nights):
            for idx in range(len(self.hotels)):
                self.pheromones[night][idx] *= 1 - self.evaporation
        # Depósito
        for solution, fit in zip(solutions, fitnesses):
            for night, hotel in enumerate(solution):
                idx = self.hotels.index(hotel)
                self.pheromones[night][idx] += fit

    def search_best_path(self) -> Tuple[List[Hotel], float]:
        """
        Ejecuta el algoritmo ACO para encontrar el mejor itinerario de hoteles.
        Devuelve la mejor solución y su fitness.
        """
        best_solution = []
        best_fitness = float("-inf")
        for _ in range(self.num_iter):
            solutions = []
            fitnesses = []
            for _ in range(self.num_ants):
                solution = self.construct_solution()
                fit = calcular_fitness(
                    solution,
                    self.max_hotel_stars,
                    self.budget,
                    self.alpha,
                    self.beta,
                    self.gamma,
                )
                solutions.append(solution)
                fitnesses.append(fit)
                if fit > best_fitness:
                    best_fitness = fit
                    best_solution = solution
            self.update_pheromones(solutions, fitnesses)
        return best_solution, best_fitness
