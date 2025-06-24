import numpy as np
import matplotlib.pyplot as plt
from scipy.stats import kstest, norm

# Datos de latencias y largos de respuestas
latencies = [52.66, 30.47, 47.86, 62.67, 61.18, 32.49, 74.69, 29.35, 28.75, 29.77]
lengths = [74, 61, 99, 141, 138, 52, 183, 45, 76, 56]

n_bootstrap = 10000
np.random.seed(42)

# Bootstrap para latencias
bootstrap_latencies = [
    np.mean(np.random.choice(latencies, size=len(latencies), replace=True))
    for _ in range(n_bootstrap)
]

# Bootstrap para largos de respuesta
bootstrap_lengths = [
    np.mean(np.random.choice(lengths, size=len(lengths), replace=True))
    for _ in range(n_bootstrap)
]

# Graficar distribuciones y guardar imágenes
fig, axs = plt.subplots(1, 2, figsize=(12, 5))

axs[0].hist(bootstrap_latencies, bins=30, color="skyblue", edgecolor="black")
axs[0].set_title("Distribución Bootstrap de la Latencia")
axs[0].set_xlabel("Media de Latencia (s)")
axs[0].set_ylabel("Frecuencia")

axs[1].hist(bootstrap_lengths, bins=30, color="salmon", edgecolor="black")
axs[1].set_title("Distribución Bootstrap del Largo de Respuesta")
axs[1].set_xlabel("Media de Largo de Respuesta")
axs[1].set_ylabel("Frecuencia")

plt.tight_layout()
fig.savefig("bootstrap_rag_distribuciones.png")
plt.show()

# Boxplots
fig2, axs2 = plt.subplots(1, 2, figsize=(10, 5))
axs2[0].boxplot(
    bootstrap_latencies,
    vert=False,
    patch_artist=True,
    boxprops=dict(facecolor="skyblue"),
    showfliers=False,
)
axs2[0].set_title("Boxplot de la Latencia (Bootstrap)")
axs2[0].set_xlabel("Media de Latencia (s)")

axs2[1].boxplot(
    bootstrap_lengths,
    vert=False,
    patch_artist=True,
    boxprops=dict(facecolor="salmon"),
    showfliers=False,
)
axs2[1].set_title("Boxplot del Largo de Respuesta (Bootstrap)")
axs2[1].set_xlabel("Media de Largo de Respuesta")

plt.tight_layout()
fig2.savefig("bootstrap_rag_boxplots.png")
plt.show()

# Estadísticos
print("Resultados Bootstrap (RAG):")
print(
    f"Latencia - Media: {np.mean(bootstrap_latencies):.4f}, Varianza: {np.var(bootstrap_latencies):.6f}"
)
print(
    f"Largo   - Media: {np.mean(bootstrap_lengths):.4f}, Varianza: {np.var(bootstrap_lengths):.6f}"
)

# Test de Kolmogorov-Smirnov para la normalidad
ks_latencies = kstest(
    bootstrap_latencies,
    "norm",
    args=(np.mean(bootstrap_latencies), np.std(bootstrap_latencies)),
)
ks_lengths = kstest(
    bootstrap_lengths,
    "norm",
    args=(np.mean(bootstrap_lengths), np.std(bootstrap_lengths)),
)

print("\nTest de Kolmogorov-Smirnov para la normalidad (nivel de confianza 0.95):")
if ks_latencies.pvalue > 0.05:
    print(f"Latencia: No se rechaza la normalidad (p = {ks_latencies.pvalue:.4f})")
else:
    print(f"Latencia: Se rechaza la normalidad (p = {ks_latencies.pvalue:.4f})")

if ks_lengths.pvalue > 0.05:
    print(f"Largo: No se rechaza la normalidad (p = {ks_lengths.pvalue:.4f})")
else:
    print(f"Largo: Se rechaza la normalidad (p = {ks_lengths.pvalue:.4f})")
