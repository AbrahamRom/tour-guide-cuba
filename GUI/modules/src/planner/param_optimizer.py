import sys
import os
import csv
import random
import optuna
import pandas as pd
import numpy as np
from src.data.hotel_repository import HotelRepository
from src.planner.aco_planner import ACOPlanner
from src.planner.pso_planner import PSOPlanner


# -------------------- Utilidades de generación de pesos y parámetros --------------------
def random_weights() -> list:
    """
    Genera tres pesos aleatorios positivos que suman 3.0.
    """
    vals = [random.uniform(0.5, 2.0) for _ in range(3)]
    s = sum(vals)
    return [v * 3.0 / s for v in vals]


def random_experiment_params() -> tuple:
    """
    Genera parámetros aleatorios para un experimento (noches, presupuesto, destino).
    """
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


def random_weights_and_params() -> tuple:
    """
    Genera pesos y parámetros aleatorios para un experimento.
    """
    alpha, beta, gamma = random_weights()
    nights, budget, destino = random_experiment_params()
    return alpha, beta, gamma, nights, budget, destino


# -------------------- Optimizadores de parámetros para PSO y ACO --------------------
def optimize_pso(repo: HotelRepository, n_trials=30):
    """
    Optimiza los parámetros de PSO usando Optuna.
    """
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
    return study.best_params, -study.best_value, best_trial.user_attrs


def optimize_aco(repo: HotelRepository, n_trials=30):
    """
    Optimiza los parámetros de ACO usando Optuna.
    """
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
    return study.best_params, -study.best_value, best_trial.user_attrs


# -------------------- Ejecución de experimentos masivos --------------------
def run_experiments(n_experiments=100, output_file="experiment_results.csv"):
    """
    Ejecuta múltiples experimentos de optimización y guarda los resultados en un CSV.
    """
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


# -------------------- Utilidades de análisis de resultados --------------------
def get_mode_rounded(csv_file, column, decimals=2):
    """
    Calcula la moda de una columna numérica racional redondeando los valores.
    """
    df = pd.read_csv(csv_file)
    rounded = df[column].round(decimals)
    return rounded.mode()[0]


def get_histogram_mode(csv_file, column, bin_width=0.05):
    """
    Encuentra el intervalo más frecuente (bin) de una columna numérica racional usando histogramas.
    """
    df = pd.read_csv(csv_file)
    min_val = df[column].min()
    max_val = df[column].max()
    bins = np.arange(min_val, max_val + bin_width, bin_width)
    counts, bin_edges = np.histogram(df[column], bins=bins)
    max_bin_index = np.argmax(counts)
    return (bin_edges[max_bin_index], bin_edges[max_bin_index + 1])


def get_discrete_mode(csv_file, column):
    """
    Calcula la moda de una columna discreta (entera) en un archivo CSV.
    """
    df = pd.read_csv(csv_file)
    return df[column].mode()[0]


# -------------------- Ejemplo de uso directo --------------------
if __name__ == "__main__":
    # run_experiments()
    mode_aco_num_ants = get_discrete_mode("experiment_results.csv", "aco_num_ants")
    mode_pso_num_particles = get_discrete_mode(
        "experiment_results.csv", "pso_num_particles"
    )
    print("Moda aco_num_ants:", mode_aco_num_ants)
    print("Moda pso_num_particles:", mode_pso_num_particles)
    df = pd.read_csv("experiment_results.csv")
    # Crear un histograma con bins de 0.05 (ajusta según tus datos)
    counts, bins = np.histogram(df["aco_evaporation"], bins=np.arange(0, 1.05, 0.05))
    max_bin_index = np.argmax(counts)
    best_interval = (bins[max_bin_index], bins[max_bin_index + 1])
    print(f"Intervalo más frecuente para aco_evaporation: {best_interval}")
    # Redondear a 2 decimales (puedes ajustar esto)
    rounded = df["aco_evaporation"].round(3)
    best_value = rounded.mode()[0]
    print(f"Valor más frecuente (redondeado) para aco_evaporation: {best_value}")
