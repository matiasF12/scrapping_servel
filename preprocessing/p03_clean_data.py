# Librerias
#%%
import os
import pandas as pd
import argparse
import sys, os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(BASE_DIR)

from functions.parameters import pacto_map
from functions.funciones_extras import normalizar_tipo_eleccion, procesar_regiones
from functions.utils import prepare_sys_argv_for_interactive
prepare_sys_argv_for_interactive()

# Parametros
parser = argparse.ArgumentParser(description="Scraper SERVEL - Chile")
parser.add_argument("--tipo", type=str, default="diputados", choices=["diputados", "senadores"], help="Tipo de elección a scrapear (default: diputados)")
parser.add_argument("--regiones", type=str, default="todas", help='Regiones a scrapear. Ej: "todas", "METROPOLITANA DE SANTIAGO". Default: METROPOLITANA DE SANTIAGO')
args = parser.parse_args()


# Parametros normalizados
TIPO_ELECCION = normalizar_tipo_eleccion(args.tipo)  # Devuelve Diputados, Senadores, Presidente
REGIONES_INPUT = args.regiones

# para reconstruir nombre del archivo
regiones_norm = REGIONES_INPUT.lower().replace(" ", "_")
tipo_norm = args.tipo.lower()

# archivo = f"files/datasets/intermedia/{tipo_norm}_{regiones_norm}.csv"

# print(f"Intentando cargar archivo: {archivo}")

# if not os.path.exists(archivo):
#     raise FileNotFoundError(
#         f"⚠ El archivo no existe: {archivo}\n"
#         f"Asegúrate de haber ejecutado el scrapper correspondiente."
#     )


path_distritos = os.path.join(
    BASE_DIR,
    "files",
    "datasets",
    "input",
    "Territorios Electorales.xlsx"
)

archivo = os.path.join(
    BASE_DIR,
    "files",
    "datasets",
    "intermedia",
    f"{tipo_norm}_{regiones_norm}.csv"
)

if not os.path.exists(path_distritos):
    raise FileNotFoundError(f"No se encontró: {path_distritos}")

# ============================================================
# CARGAR CSV
# ============================================================

df_original = pd.read_csv(archivo)
df_distritos = pd.read_excel(path_distritos)
#df_distritos = pd.read_excel('files/datasets/input/Territorios Electorales.xlsx')

print("✔ Archivo cargado correctamente!")
print(df_original.head())

#%%

# Limpieza columna candidatos
df = df_original.copy()

# 1) Identificar candidatos (True / False)
df["es_candidato"] = df["lista_pacto"].fillna("").str.match(r"^\d+\s+")

# Convertir a boolean real
df["es_candidato"] = df["es_candidato"].fillna(False).astype(bool)

df["candidatos"] =  pd.NA
df.loc[df["es_candidato"], "candidatos"] = df.loc[df["es_candidato"], "lista_pacto"]
df["candidatos"] = df["candidatos"].str.replace(r"^\d+\s+", "", regex=True)
df = df[df["candidatos"].notna()]

# Construir pacto
df["pacto"] = df["partido"].map(pacto_map)

#TODO: ACA VOY
# Normalizar comuna
df["comuna"] = df["comuna"].apply(normalizar_nombre)

# ---- 4. LIMPIAR PORCENTAJE ----
df["porcentaje"] = (
    df["porcentaje"]
    .str.replace("%", "", regex=False)
    .str.replace(",", ".", regex=False)
    .astype(float)
)