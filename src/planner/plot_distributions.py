import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# Cargar el archivo CSV
df = pd.read_csv("experiment_results.csv")

# Configuración de estilo
title_font = {"fontsize": 14, "fontweight": "bold"}
sns.set(style="whitegrid")

# Gráfica de distribución para pso_num_particles
plt.figure(figsize=(8, 4))
sns.histplot(df["pso_num_particles"], kde=True, bins=15, color="skyblue")
plt.title("Distribución de pso_num_particles", **title_font)
plt.xlabel("pso_num_particles")
plt.ylabel("Frecuencia")
plt.tight_layout()
plt.savefig("pso_num_particles_dist.png")
plt.close()

# Gráfica de distribución para aco_num_ants
plt.figure(figsize=(8, 4))
sns.histplot(df["aco_num_ants"], kde=True, bins=15, color="salmon")
plt.title("Distribución de aco_num_ants", **title_font)
plt.xlabel("aco_num_ants")
plt.ylabel("Frecuencia")
plt.tight_layout()
plt.savefig("aco_num_ants_dist.png")
plt.close()

# Gráfica de distribución para aco_evaporation
plt.figure(figsize=(8, 4))
sns.histplot(df["aco_evaporation"], kde=True, bins=15, color="mediumseagreen")
plt.title("Distribución de aco_evaporation", **title_font)
plt.xlabel("aco_evaporation")
plt.ylabel("Frecuencia")
plt.tight_layout()
plt.savefig("aco_evaporation_dist.png")
plt.close()

print(
    "Gráficas guardadas como pso_num_particles_dist.png, aco_num_ants_dist.png y aco_evaporation_dist.png"
)
