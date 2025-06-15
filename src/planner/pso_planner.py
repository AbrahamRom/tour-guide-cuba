from typing import List, Tuple
import random
import numpy as np
from src.data.hotel import Hotel
from src.data.hotel_repository import HotelRepository
from src.planner.fitness import calcular_fitness


class PSOPlanner:
    def __init__(
        self,
        hotel_repo: HotelRepository,
        nights: int,
        budget: float,
        destino: str,
        num_particles=42,  # Dado por el ajuste de parametros
        num_iter=300,
        alpha=1.0,
        beta=1.0,
        gamma=1.0,
        w=0.7,  # Inercia
        c1=1.5,  # Cognitivo
        c2=1.5,  # Social
    ):
        self.hotel_repo = hotel_repo
        self.nights = nights
        self.budget = budget
        self.destino = destino
        self.num_particles = num_particles
        self.num_iter = num_iter
        self.alpha = alpha
        self.beta = beta
        self.gamma = gamma
        self.w = w
        self.c1 = c1
        self.c2 = c2
        self.hotels = self.hotel_repo.get_hotels_by_destino(destino)
        self.max_hotel_stars = max((h.stars for h in self.hotels), default=1)
        self.num_hotels = len(self.hotels)

    def _random_solution(self) -> List[int]:
        solution = []
        budget_left = self.budget
        for _ in range(self.nights):
            valid = [i for i, h in enumerate(self.hotels) if h.price <= budget_left]
            if not valid:
                break
            idx = random.choice(valid)
            solution.append(idx)
            budget_left -= self.hotels[idx].price
        while len(solution) < self.nights:
            solution.append(solution[-1] if solution else 0)
        return solution

    def _solution_to_hotels(self, solution: List[int]) -> List[Hotel]:
        return [self.hotels[i] for i in solution]

    def search_best_path(self) -> Tuple[List[Hotel], float]:
        particles = [self._random_solution() for _ in range(self.num_particles)]
        velocities = [np.zeros(self.nights) for _ in range(self.num_particles)]
        personal_best = [p[:] for p in particles]
        personal_best_fitness = [
            calcular_fitness(
                self._solution_to_hotels(sol),
                self.max_hotel_stars,
                self.budget,
                self.alpha,
                self.beta,
                self.gamma,
            )
            for sol in particles
        ]
        global_best_idx = int(np.argmax(personal_best_fitness))
        global_best = personal_best[global_best_idx][:]
        global_best_fitness = personal_best_fitness[global_best_idx]

        for _ in range(self.num_iter):
            for i in range(self.num_particles):
                for d in range(self.nights):
                    r1, r2 = random.random(), random.random()
                    velocities[i][d] = (
                        self.w * velocities[i][d]
                        + self.c1 * r1 * (personal_best[i][d] - particles[i][d])
                        + self.c2 * r2 * (global_best[d] - particles[i][d])
                    )
                    if random.random() < 1 / (1 + np.exp(-velocities[i][d])):
                        budget_left = self.budget - sum(
                            self.hotels[particles[i][j]].price for j in range(d)
                        )
                        valid = [
                            idx
                            for idx, h in enumerate(self.hotels)
                            if h.price <= budget_left
                        ]
                        if valid:
                            particles[i][d] = random.choice(valid)
                budget_used = 0
                for d in range(self.nights):
                    price = self.hotels[particles[i][d]].price
                    if budget_used + price > self.budget:
                        valid = [
                            idx
                            for idx, h in enumerate(self.hotels)
                            if h.price + budget_used <= self.budget
                        ]
                        if valid:
                            particles[i][d] = min(
                                valid, key=lambda idx: self.hotels[idx].price
                            )
                        else:
                            particles[i][d] = 0
                    budget_used += self.hotels[particles[i][d]].price
                hotels_sol = self._solution_to_hotels(particles[i])
                fit = calcular_fitness(
                    hotels_sol,
                    self.max_hotel_stars,
                    self.budget,
                    self.alpha,
                    self.beta,
                    self.gamma,
                )
                if fit > personal_best_fitness[i]:
                    personal_best[i] = particles[i][:]
                    personal_best_fitness[i] = fit
                    if fit > global_best_fitness:
                        global_best = particles[i][:]
                        global_best_fitness = fit

        best_hotels = self._solution_to_hotels(global_best)
        return best_hotels, global_best_fitness
