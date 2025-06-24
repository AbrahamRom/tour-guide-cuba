import numpy as np
import matplotlib.pyplot as plt
from scipy.stats import kstest, norm

# Datos originales
calidad = [
    0.9181373759872521,
    0.8988856617646735,
    0.7579348081429641,
    0.7832744226860998,
    0.7092972666062742,
    0.965909208801358,
    0.9098648783989222,
    0.9137165481377176,
    0.5353327238711127,
    0.8505905314622926,
    0.9518172686249529,
    0.7880969063818771,
    0.7612209080459371,
    0.579738671537666,
    0.8143434374070517,
    0.624536084091682,
    0.6625341362329031,
    0.7655251108742782,
    0.9027763943195654,
    0.9261771495388597,
    0.9743297186457875,
    0.9386965970640723,
    0.9393573459421237,
    0.9055499650942066,
    0.9293312879851608,
    0.859645089879272,
    0.8835711043448523,
    0.9080484167948175,
    0.7371015373012508,
    0.82341180180217,
]

tiempos = [
    161.22346472740173,
    161.0608549118042,
    164.72537851333618,
    159.11917543411255,
    155.89228558540344,
    149.81062984466553,
    151.62447428703308,
    158.68609309196472,
    158.4304006099701,
    160.2461302280426,
    161.61199855804443,
    162.66374373435974,
    157.94913482666016,
    163.65602350234985,
    155.56490015983582,
    156.1526973247528,
    153.34791493415833,
    153.26895356178284,
    156.83847332000732,
    157.19236016273499,
    162.55952620506287,
    158.04627966880798,
    152.5321068763733,
    156.39088487625122,
    151.84752464294434,
    156.09970140457153,
    154.7845664024353,
    153.51773810386658,
    158.83576703071594,
    155.39618134498596,
]

# Parámetros de bootstrap
n_bootstrap = 10000
np.random.seed(42)

# Bootstrap para calidad
bootstrap_calidad = [
    np.mean(np.random.choice(calidad, size=len(calidad), replace=True))
    for _ in range(n_bootstrap)
]

# Bootstrap para tiempos
bootstrap_tiempos = [
    np.mean(np.random.choice(tiempos, size=len(tiempos), replace=True))
    for _ in range(n_bootstrap)
]

# Graficar distribuciones y guardar imágenes
fig, axs = plt.subplots(1, 2, figsize=(12, 5))

axs[0].hist(bootstrap_calidad, bins=30, color="skyblue", edgecolor="black")
axs[0].set_title("Distribución Bootstrap de la Calidad")
axs[0].set_xlabel("Media de Calidad")
axs[0].set_ylabel("Frecuencia")

axs[1].hist(bootstrap_tiempos, bins=30, color="salmon", edgecolor="black")
axs[1].set_title("Distribución Bootstrap del Tiempo")
axs[1].set_xlabel("Media de Tiempo (s)")
axs[1].set_ylabel("Frecuencia")

plt.tight_layout()
fig.savefig(
    "bootstrap_distribuciones.png"
)  # Guarda ambas distribuciones en una sola imagen
plt.show()

# Gráficos de cajas y bigotes (boxplot) sin valores extremos (outliers)
fig2, axs2 = plt.subplots(1, 2, figsize=(10, 5))

axs2[0].boxplot(
    bootstrap_calidad,
    vert=False,
    patch_artist=True,
    boxprops=dict(facecolor="skyblue"),
    showfliers=False,
)
axs2[0].set_title("Boxplot de la Calidad (Bootstrap)")
axs2[0].set_xlabel("Media de Calidad")

axs2[1].boxplot(
    bootstrap_tiempos,
    vert=False,
    patch_artist=True,
    boxprops=dict(facecolor="salmon"),
    showfliers=False,
)
axs2[1].set_title("Boxplot del Tiempo (Bootstrap)")
axs2[1].set_xlabel("Media de Tiempo (s)")

plt.tight_layout()
fig2.savefig("bootstrap_boxplots.png")  # Guarda los boxplots en una imagen
plt.show()

# Mostrar media y varianza de las distribuciones bootstrap
print("Resultados Bootstrap:")
print(
    f"Calidad - Media: {np.mean(bootstrap_calidad):.4f}, Varianza: {np.var(bootstrap_calidad):.6f}"
)
print(
    f"Tiempo  - Media: {np.mean(bootstrap_tiempos):.4f}, Varianza: {np.var(bootstrap_tiempos):.6f}"
)

# Test de Kolmogorov-Smirnov para la normalidad
ks_calidad = kstest(
    bootstrap_calidad,
    "norm",
    args=(np.mean(bootstrap_calidad), np.std(bootstrap_calidad)),
)
ks_tiempos = kstest(
    bootstrap_tiempos,
    "norm",
    args=(np.mean(bootstrap_tiempos), np.std(bootstrap_tiempos)),
)

print("\nTest de Kolmogorov-Smirnov para la normalidad (nivel de confianza 0.95):")
if ks_calidad.pvalue > 0.05:
    print(f"Calidad: No se rechaza la normalidad (p = {ks_calidad.pvalue:.4f})")
else:
    print(f"Calidad: Se rechaza la normalidad (p = {ks_calidad.pvalue:.4f})")

if ks_tiempos.pvalue > 0.05:
    print(f"Tiempo: No se rechaza la normalidad (p = {ks_tiempos.pvalue:.4f})")
else:
    print(f"Tiempo: Se rechaza la normalidad (p = {ks_tiempos.pvalue:.4f})")

# --- Bootstrap y análisis para los nuevos datos de calidad de recomendaciones ---
calidad_recom = [
    0.2669999897480011,
    0.35100001096725464,
    0.3400000035762787,
    0.28600001335144043,
    0.3240000009536743,
    0.2939999997615814,
    0.39899998903274536,
    0.33899998664855957,
    0.2879999876022339,
    0.43700000643730164,
]

# Bootstrap para calidad de recomendaciones
bootstrap_calidad_recom = [
    np.mean(np.random.choice(calidad_recom, size=len(calidad_recom), replace=True))
    for _ in range(n_bootstrap)
]

# Graficar distribución e imagen
fig3, axs3 = plt.subplots(1, 2, figsize=(12, 5))
axs3[0].hist(
    bootstrap_calidad_recom, bins=30, color="mediumseagreen", edgecolor="black"
)
axs3[0].set_title("Distribución Bootstrap Calidad Recomendaciones")
axs3[0].set_xlabel("Media de Calidad")
axs3[0].set_ylabel("Frecuencia")
axs3[1].boxplot(
    bootstrap_calidad_recom,
    vert=False,
    patch_artist=True,
    boxprops=dict(facecolor="mediumseagreen"),
    showfliers=False,
)
axs3[1].set_title("Boxplot Calidad Recomendaciones (Bootstrap)")
axs3[1].set_xlabel("Media de Calidad")
plt.tight_layout()
fig3.savefig("bootstrap_calidad_recom.png")
plt.show()

# Estadísticos
print("\nResultados Bootstrap (Calidad Recomendaciones):")
print(
    f"Media: {np.mean(bootstrap_calidad_recom):.4f}, Varianza: {np.var(bootstrap_calidad_recom):.6f}"
)

# Test de Kolmogorov-Smirnov para la normalidad
ks_calidad_recom = kstest(
    bootstrap_calidad_recom,
    "norm",
    args=(np.mean(bootstrap_calidad_recom), np.std(bootstrap_calidad_recom)),
)
if ks_calidad_recom.pvalue > 0.05:
    print(
        f"Calidad Recomendaciones: No se rechaza la normalidad (p = {ks_calidad_recom.pvalue:.4f})"
    )
else:
    print(
        f"Calidad Recomendaciones: Se rechaza la normalidad (p = {ks_calidad_recom.pvalue:.4f})"
    )
