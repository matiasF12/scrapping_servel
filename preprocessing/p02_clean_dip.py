#%%
import sys
import os
import time
import random
import re
import pandas as pd
import numpy as np
import openpyxl
import unicodedata

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

#%% Input
path_csv = os.path.join(BASE_DIR, "files", "datasets", "intermedia", "diputados_rm_ok.csv")
df_dip = pd.read_csv(path_csv)

path_distritos = os.path.join(BASE_DIR, "files", "datasets", "input", "Territorios Electorales.xlsx")
df_distritos = pd.read_excel(path_distritos)

#%%

#%% ------------------ FUNCIONES ------------------

def empieza_con_numero(texto):
    return bool(re.match(r"^\d+", str(texto).strip()))

# Normalizar textos
def normalizar_nombre(x):
    if pd.isna(x):
        return ""
    x = str(x).strip().upper()
    x = x.replace("Ñ", "N")
    x = unicodedata.normalize("NFKD", x).encode("ascii", "ignore").decode("utf-8")
    return x

# Limpiar votos
def limpiar_votos(x):
    x = str(x).strip()

    # Caso 1: 717.0 → 717
    if re.match(r"^\d+\.0$", x):
        return int(float(x))

    # Caso 2: 2.026 → 2026
    if re.match(r"^\d{1,3}(\.\d{3})+$", x):
        return int(x.replace(".", ""))

    # Caso 3: entero simple
    if x.isdigit():
        return int(x)

    try:
        return int(float(x))
    except:
        return np.nan

#%% ------------------ PROCESAMIENTO ------------------

df = df_dip.copy()

# ---- 🔥 1. CREAR COLUMNA PACTO ----
df["pacto"] = None

# Filas que son pactos (NO empiezan con número)
es_pacto = ~df["lista_pacto"].astype(str).str.strip().str.match(r"^\d+")

# Guardar el pacto en esas filas
df.loc[es_pacto, "pacto"] = df.loc[es_pacto, "lista_pacto"].str.strip()

# Rellenar hacia abajo el pacto para asignarlo a los candidatos
df["pacto"] = df["pacto"].ffill()

# Eliminar filas que son encabezado de pacto
df = df[~es_pacto].copy()

# ---- 2. LIMPIAR VOTOS ----
df["votos"] = df["votos"].apply(limpiar_votos)

# ---- 3. RENOMBRAR candidato ----
df = df.rename(columns={"lista_pacto": "candidato"})

# Quitar número inicial
df["candidato"] = df["candidato"].str.replace(r"^\d+\s+", "", regex=True)

# Normalizar comuna
df["comuna"] = df["comuna"].apply(normalizar_nombre)

# ---- 4. LIMPIAR PORCENTAJE ----
df["porcentaje"] = (
    df["porcentaje"]
    .str.replace("%", "", regex=False)
    .str.replace(",", ".", regex=False)
    .astype(float)
)

# ---- 5. JOIN CON DISTRITOS ----
df_distritos["Comuna"] = df_distritos["Comuna"].apply(normalizar_nombre)
df_distritos = df_distritos.rename(columns={"Comuna": "comuna"})
df_distritos_filter = df_distritos[['comuna', 'Distrito']]

df_final = df.merge(df_distritos_filter, on="comuna", how="left")

# Asegurar votos como entero
df_final['votos'] = df_final['votos'].astype("Int64")

#%% Exportar
path_output = os.path.join(BASE_DIR, "files", "datasets", "output", "diputados_rm_grid_limpio.csv")
df_final.to_csv(path_output, index=False)

print(f"Archivo exportado en: {path_output}")