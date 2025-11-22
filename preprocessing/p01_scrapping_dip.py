# DIPUTADOS Y SENADORES
import time
import random
import pandas as pd
import argparse

from selenium import webdriver
from selenium.webdriver import Chrome
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
from functions.scrapping import pausa, extraer_tabla_js, esperar_actualizacion_tabla, get_selects, esperar_select_habilitado, construir_dataframe
from functions.funciones_extras import normalizar_tipo_eleccion, normalizar_region, procesar_regiones, opciones_habilitadas

# ============================================================
# PARAMETROS
# ============================================================

parser = argparse.ArgumentParser(description="Scraper SERVEL - Chile")
parser.add_argument("--tipo", type=str, default="senadores", choices=["diputados", "senadores"], help="Tipo de elección a scrapear (default: diputados)")
parser.add_argument("--regiones", type=str, default="todas", help='Regiones a scrapear. Ej: "todas", "RM", "RM,BIOBIO", "METROPOLITANA DE SANTIAGO". Default: METROPOLITANA DE SANTIAGO')
args = parser.parse_args()

# ============================================================
# PARAMETROS DERIVADOS
# ============================================================

TIPO_ELECCION = normalizar_tipo_eleccion(args.tipo)
REGIONES_INPUT = args.regiones

# --- Normalización de regiones ---
REGIONES = procesar_regiones(args.regiones)

# --- Texto del botón usando TIPO_ELECCION ya normalizado ---
texto_boton = TIPO_ELECCION

# ============================================================
# CONFIGURAR NAVEGADOR
# ============================================================

service = Service(ChromeDriverManager().install())
options = webdriver.ChromeOptions()
options.add_argument("--window-size=1920,1080")

driver = Chrome(service=service, options=options)
driver.get("https://elecciones.servel.cl")
time.sleep(2)

# ============================================================
# CLICK EN SELECCION
# ============================================================

for b in driver.find_elements(By.TAG_NAME, "button"):
    if texto_boton in b.text:
        b.click()
        break

time.sleep(1)

driver.find_element(By.XPATH, "//button[contains(., 'División Geográfica Chile')]").click()
time.sleep(1.2)

# ============================================================
# SCRAPING
# ============================================================

select_region, select_provincia, select_comuna = get_selects(driver)
todas_las_regiones = [o.text for o in select_region.options if o.text != "Seleccionar"]

regiones_filtradas = []

for r in REGIONES:
    if r in todas_las_regiones:
        regiones_filtradas.append(r)
    else:
        print(f"⚠️ Advertencia: La región '{r}' no está disponible para esta elección. Se omite.")

regiones = regiones_filtradas

data_final = []
ultima_tabla = None

# Loop
for region in regiones:  # regiones ya viene filtrado antes

    # Filtrar regiones habilitadas dinámicamente
    regiones_hab = opciones_habilitadas(select_region)
    if region not in regiones_hab:
        print(f"⚠ Región DESHABILITADA en Servel: {region} (omitida)")
        continue

    select_region.select_by_visible_text(region)
    pausa()

    # ======================================================
    # 1) PROVINCIAS DESPUÉS DE SELECCIONAR LA REGIÓN
    # ======================================================
    _, select_provincia, _ = get_selects(driver)
    provincias_hab = opciones_habilitadas(select_provincia)

    for provincia in provincias_hab:
        select_provincia.select_by_visible_text(provincia)
        pausa()

        # ======================================================
        # 2) COMUNAS DESPUÉS DE SELECCIONAR LA PROVINCIA
        # ======================================================
        _, _, select_comuna = get_selects(driver)
        comunas_hab = opciones_habilitadas(select_comuna)

        for comuna in comunas_hab:
            select_comuna.select_by_visible_text(comuna)
            pausa()

            print(f"📍 Procesando → Región: {region} | Provincia: {provincia} | Comuna: {comuna}")

            # Esperar actualización real de la tabla
            rows = esperar_actualizacion_tabla(driver, ultima_tabla=ultima_tabla)

            if len(rows) == 0:
                print("⚠ SIN TABLA ->", comuna)
                continue

            if ultima_tabla is not None and rows == ultima_tabla:
                print("⚠ TABLA REPETIDA ->", comuna)
                continue

            ultima_tabla = rows

            df = construir_dataframe(
                rows=rows,
                tipo=TIPO_ELECCION,
                region=region,
                provincia=provincia,
                comuna=comuna
            )

            data_final.append(df)

# ============================================================
# GUARDAR
# ============================================================

regiones_norm = REGIONES_INPUT.lower().replace(" ", "_")
tipo_norm = TIPO_ELECCION.lower()

nombre_salida = f"{tipo_norm}_{regiones_norm}.csv"
ruta_salida = f"files/datasets/intermedia/{nombre_salida}"

if len(data_final) == 0:
    print("⚠ No se obtuvo ninguna tabla. No se genera archivo.")
else:
    df_final = pd.concat(data_final, ignore_index=True)
    df_final.to_csv(ruta_salida, index=False)
    print(f"✔ FIN - Guardado en: {ruta_salida}")


driver.quit()

