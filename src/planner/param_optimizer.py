import sys
import os
import csv

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

import optuna
import random
from src.data.hotel_repository import HotelRepository
from src.planner.aco_planner import ACOPlanner
from src.planner.pso_planner import PSOPlanner


def random_weights():
    # Genera tres pesos aleatorios positivos que suman 3.0 (o puedes usar otra suma)
    vals = [random.uniform(0.5, 2.0) for _ in range(3)]
    s = sum(vals)
    return [v * 3.0 / s for v in vals]


def optimize_pso(repo: HotelRepository, n_trials=30):

    alpha, beta, gamma, nights, budget, destino = random_weights_and_params()

    def objective(trial):
        num_particles = trial.suggest_int("num_particles", 10, 50)
        trial.set_user_attr("alpha", alpha)
        trial.set_user_attr("beta", beta)
        trial.set_user_attr("gamma", gamma)
        trial.set_user_attr("nights", nights)
        trial.set_user_attr("budget", budget)
        trial.set_user_attr("destino", destino)
        planner = PSOPlanner(
            repo,
            nights,
            budget,
            destino,
            num_particles=num_particles,
            num_iter=40,
            alpha=alpha,
            beta=beta,
            gamma=gamma,
        )
        solution, fitness = planner.search_best_path()
        return -fitness  # Negativo para maximizar

    study = optuna.create_study(direction="minimize")
    study.optimize(objective, n_trials=n_trials)
    best_trial = study.best_trial
    print("Mejores parámetros PSO:", study.best_params)
    # print(
    #     f"alpha: {best_trial.user_attrs['alpha']:.3f}, beta: {best_trial.user_attrs['beta']:.3f}, gamma: {best_trial.user_attrs['gamma']:.3f}"
    # )
    # print(
    #     f"nights: {best_trial.user_attrs['nights']}, budget: {best_trial.user_attrs['budget']}, destino: {best_trial.user_attrs['destino']}"
    # )
    return study.best_params, -study.best_value, best_trial.user_attrs


def optimize_aco(repo: HotelRepository, n_trials=30):

    alpha, beta, gamma, nights, budget, destino = random_weights_and_params()

    def objective(trial):
        num_ants = trial.suggest_int("num_ants", 10, 50)
        evaporation = trial.suggest_float("evaporation", 0.1, 0.9)
        trial.set_user_attr("alpha", alpha)
        trial.set_user_attr("beta", beta)
        trial.set_user_attr("gamma", gamma)
        trial.set_user_attr("nights", nights)
        trial.set_user_attr("budget", budget)
        trial.set_user_attr("destino", destino)
        planner = ACOPlanner(
            repo,
            nights,
            budget,
            destino,
            num_ants=num_ants,
            num_iter=40,
            alpha=alpha,
            beta=beta,
            gamma=gamma,
            evaporation=evaporation,
        )
        solution, fitness = planner.search_best_path()
        return -fitness

    study = optuna.create_study(direction="minimize")
    study.optimize(objective, n_trials=n_trials)
    best_trial = study.best_trial
    print("Mejores parámetros ACO:", study.best_params)
    # print(
    #     f"alpha: {best_trial.user_attrs['alpha']:.3f}, beta: {best_trial.user_attrs['beta']:.3f}, gamma: {best_trial.user_attrs['gamma']:.3f}"
    # )
    # print(
    #     f"nights: {best_trial.user_attrs['nights']}, budget: {best_trial.user_attrs['budget']}, destino: {best_trial.user_attrs['destino']}"
    # )
    return study.best_params, -study.best_value, best_trial.user_attrs


def random_experiment_params():
    nights = random.randint(3, 10)
    budget = random.randint(200, 1500)
    destinos = [
        "La Habana",
        "Varadero",
        "Camagüey",
        "Matanzas",
        "Ciego de Ávila",
        "Holguín",
        "Santiago",
        "Cienfuegos",
        "Santa Maria",
    ]
    destino = random.choice(destinos)
    return nights, budget, destino


def random_weights_and_params():
    alpha, beta, gamma = random_weights()
    nights, budget, destino = random_experiment_params()
    return alpha, beta, gamma, nights, budget, destino


def run_experiments(n_experiments=1000, output_file="experiment_results.csv"):
    results = []
    repo = HotelRepository.from_csv(
        r"e:/Universidad/3er Año/2do Semestre/Proyecto Conjunto/tour-guide-cuba/tourism_data.csv"
    )
    for i in range(n_experiments):
        nights, budget, destino = random_experiment_params()
        print(
            f"\nExperimento {i+1}: nights={nights}, budget={budget}, destino={destino}"
        )
        best_pso_params, best_pso_fitness, best_pso_weights = optimize_pso(
            repo, n_trials=100
        )
        best_aco_params, best_aco_fitness, best_aco_weights = optimize_aco(
            repo, n_trials=100
        )
        results.append(
            {
                "exp": i + 1,
                "nights": nights,
                "budget": budget,
                "destino": destino,
                "pso_num_particles": best_pso_params.get("num_particles"),
                "pso_alpha": best_pso_weights["alpha"],
                "pso_beta": best_pso_weights["beta"],
                "pso_gamma": best_pso_weights["gamma"],
                "pso_fitness": best_pso_fitness,
                "aco_num_ants": best_aco_params.get("num_ants"),
                "aco_evaporation": best_aco_params.get("evaporation"),
                "aco_alpha": best_aco_weights["alpha"],
                "aco_beta": best_aco_weights["beta"],
                "aco_gamma": best_aco_weights["gamma"],
                "aco_fitness": best_aco_fitness,
            }
        )
    # Guardar resultados en CSV
    with open(output_file, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(results[0].keys()))
        writer.writeheader()
        writer.writerows(results)
    print(f"\nResultados guardados en {output_file}")


# def main():
#     repo = HotelRepository.from_csv(
#         r"e:/Universidad/3er Año/2do Semestre/Proyecto Conjunto/tour-guide-cuba/tourism_data.csv"
#     )
#     nights = 7
#     budget = 800
#     destino = "La Habana"
#     print("Optimizando PSO...")
#     best_pso_params, best_pso_fitness, best_pso_weights = optimize_pso(
#         repo, nights, budget, destino, n_trials=100
#     )
#     print("Mejores parámetros PSO:", best_pso_params)
#     print("Pesos alpha, beta, gamma:", best_pso_weights)
#     print("Mejor fitness PSO:", best_pso_fitness)
#     print("\nOptimizando ACO...")
#     best_aco_params, best_aco_fitness, best_aco_weights = optimize_aco(
#         repo, nights, budget, destino, n_trials=100
#     )
#     print("Mejores parámetros ACO:", best_aco_params)
#     print("Pesos alpha, beta, gamma:", best_aco_weights)
#     print("Mejor fitness ACO:", best_aco_fitness)


if __name__ == "__main__":
    run_experiments()
