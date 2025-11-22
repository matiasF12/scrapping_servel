# GRAFICOS

import sys
import os

# Agregar la carpeta raíz del proyecto al PATH
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import time
import random
import re
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import math
from functions.funciones_extras import dhondt_distrito

from functions.graficos import (
    graficar_distribucion_comunal,
    graficar_ranking_distrito,
    graficar_distribucion_por_candidato,
    graficar_distribucion_por_comuna,
    grafico_electos_dhondt
)

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

PALETA_PACTOS = {
    "K - CAMBIO POR CHILE": "#2ECC71",                     # Verde
    "C - UNIDAD POR CHILE": "#E74C3C",                     # Rojo
    "J - CHILE GRANDE Y UNIDO": "#F1C40F",                 # Amarillo
    "B - VERDES, REGIONALISTAS Y HUMANISTAS": "#5DADE2",   # Celeste
    "I - PARTIDO DE LA GENTE": "#8E44AD",                  # Morado
}

#%% Input
path_csv = os.path.join(BASE_DIR, "files", "datasets", "output", "diputados_rm_grid_limpio.csv")
df_final = pd.read_csv(path_csv)

#%% MÉTRICAS

ranking_distrito = (
    df_final.groupby(["Distrito", "candidato"], as_index=False)["votos"]
    .sum()
    .sort_values(["Distrito", "votos"], ascending=[True, False])
)

votos_candidato = (
    df_final.groupby("candidato", as_index=False)["votos"]
    .sum()
    .sort_values("votos", ascending=False)
)

votos_region = (
    df_final.groupby("region", as_index=False)["votos"]
    .sum()
    .sort_values("votos", ascending=False)
)

votos_provincia = (
    df_final.groupby(["region", "provincia"], as_index=False)["votos"]
    .sum()
    .sort_values("votos", ascending=False)
)

votos_comuna = (
    df_final.groupby(["region", "provincia", "comuna"], as_index=False)["votos"]
    .sum()
    .sort_values("votos", ascending=False)
)

votos_partido = (
    df_final.groupby("partido", as_index=False)["votos"]
    .sum()
    .sort_values("votos", ascending=False)
)



#%% GRAFICOS+

sns.set(style="whitegrid")

# Ranking por distrito
graficar_ranking_distrito(df_final, distrito_objetivo=14, top_n=10)

# Distribucion por candidato
graficar_distribucion_por_candidato(df_final, 14, top_n=10)
graficar_distribucion_por_candidato(df_final, 10, top_n=10)

# Distribucion por coomuna
graficar_distribucion_por_comuna(df_final, 14, top_n=10)


# 

df_dh, escaños_pacto, electos = dhondt_distrito(df_final, 14)
grafico_electos_dhondt(df_final, 14, PALETA_PACTOS)

df_final[df_final["Distrito"] == 14][["pacto","candidato","votos"]].sort_values("votos", ascending=False).head(30)
df_final[df_final["Distrito"] == 14].groupby("pacto")["votos"].sum()


























# =====================================================
# 1. TOP 10 CANDIDATOS A NIVEL NACIONAL
# =====================================================

top10 = df_final.groupby(["candidato", "partido", "Distrito"], as_index=False)["votos"] \
                .sum() \
                .sort_values("votos", ascending=False) \
                .head(10)

# 2. Crear una columna combinada para mostrar mejor en el eje Y
top10["label"] = top10.apply(lambda x: f"{x['candidato']} ({x['partido']} – D{x['Distrito']})", axis=1)

# 3. Gráfico
plt.figure(figsize=(12, 8))
sns.barplot(data=top10, x="votos", y="label", palette="Blues_r")

plt.title("Top 10 candidatos más votados (Nacional)", fontsize=15)
plt.xlabel("Votos totales")
plt.ylabel("Candidato (Partido – Distrito)")
plt.tight_layout()

# 4. Agregar etiquetas de votos en las barras
for i, v in enumerate(top10["votos"]):
    plt.text(v + max(top10["votos"])*0.01,    # posición X
             i,                               # posición Y
             f"{v:,}",                         # formato con comas 10.000
             va="center")

plt.show()

# =====================================================
# 2. VOTOS POR PARTIDO (NACIONAL)
# =====================================================

plt.figure(figsize=(10, 6))
sns.barplot(data=votos_partido, x="votos", y="partido", palette="magma")
plt.title("Votos totales por partido")
plt.xlabel("Votos")
plt.ylabel("Partido")
plt.tight_layout()
plt.show()

 
# Obtener distritos únicos ordenados
distritos = sorted(ranking_distrito["Distrito"].dropna().unique())

# Cantidad de distritos
n = len(distritos)

# Definir layout (matriz de subplots)
cols = 3  # puedes modificar: 2, 3, 4
rows = math.ceil(n / cols)

fig, axes = plt.subplots(rows, cols, figsize=(18, 5 * rows), squeeze=False)

for idx, distrito in enumerate(distritos):
    df_dist = ranking_distrito[ranking_distrito["Distrito"] == distrito].head(5)

    r = idx // cols
    c = idx % cols
    ax = axes[r][c]

    sns.barplot(
        data=df_dist,
        x="votos",
        y="candidato",
        palette="viridis",
        ax=ax
    )

    ax.set_title(f"Distrito {distrito} – Top 5", fontsize=14)
    ax.set_xlabel("Votos")
    ax.set_ylabel("Candidato")

# Eliminar subplots vacíos
for j in range(idx + 1, rows * cols):
    fig.delaxes(axes[j // cols][j % cols])

plt.tight_layout()
plt.show()


#%% DISTRITO PUNTUAL

graficar_distribucion_comunal(14, df_final)
graficar_distribucion_comunal(10, df_final)
# %%
# TESTEO

df_final[df_final['candidato'] == 'JOSE ANTONIO KAST ADRIASOLA']
df_final[df_final['comuna'] == 'MELIPILLA']

votos_por_distrito = (
    df_final.groupby(["Distrito", "candidato"], as_index=False)["votos"]
    .sum()
    .sort_values(["Distrito", "votos"], ascending=[False, False])
)




#%%