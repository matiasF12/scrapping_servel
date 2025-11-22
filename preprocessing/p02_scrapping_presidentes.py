# p02 scrapping presidentes

import time
import argparse
import pandas as pd

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver import Chrome
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import Select
from bs4 import BeautifulSoup
from functions.scrapping import pausa, get_selects, extraer_tabla_presidente
from functions.funciones_extras import procesar_regiones

# ============================================================
# PARAMETROS
# ============================================================

parser = argparse.ArgumentParser(description="Scraper SERVEL - Chile")
parser.add_argument("--tipo", type=str, default="presidente", choices=["diputados", "senadores"], help="Tipo de elección a scrapear (default: diputados)")
parser.add_argument("--regiones", type=str, default="todas", help='Regiones a scrapear. Ej: "todas", "METROPOLITANA DE SANTIAGO". Default: METROPOLITANA DE SANTIAGO')
args = parser.parse_args()

# ============================================================
# PARAMETROS DERIVADOS
# ============================================================

REGIONES_INPUT = args.regiones

# Normalizar y expandir regiones
REGIONES = procesar_regiones(REGIONES_INPUT)


# ============================================================
# CONFIGURAR NAVEGADOR
# ============================================================

service = Service(ChromeDriverManager().install())
options = webdriver.ChromeOptions()
options.add_argument("--window-size=1920,1080")

driver = Chrome(service=service, options=options)
driver.get("https://elecciones.servel.cl")
pausa()

# ============================================================
# NAVEGAR A PRESIDENTE
# ============================================================

# Botón Presidente
driver.find_element(By.XPATH, '//*[@id="4"]').click()
pausa()

# Botón División Geográfica
driver.find_element(By.CSS_SELECTOR, "#filtros_boton > div:nth-child(3)").click()
pausa()

# ============================================================
# SCRAPEAR TODAS LAS REGIONES / PROVINCIAS / COMUNAS
# ============================================================

select_region, select_provincia, select_comuna = get_selects(driver)

# Todas las regiones
todas_las_regiones = [o.text for o in select_region.options if o.text != "Seleccionar"]


if REGIONES == ["TODAS"]:
    regiones = todas_las_regiones
else:
    # Filtrar solo regiones válidas
    regiones = [r for r in REGIONES if r in todas_las_regiones]

data_final = []

for region in regiones:
    select_region.select_by_visible_text(region)
    pausa()

    print(f"\n========== REGIÓN: {region} ==========")

    _, select_provincia, _ = get_selects(driver)
    provincias = [
        o.text for o in select_provincia.options
        if o.text != "Seleccionar"
    ]

    for provincia in provincias:
        select_provincia.select_by_visible_text(provincia)
        pausa()

        _, _, select_comuna = get_selects(driver)
        comunas = [
            o.text for o in select_comuna.options
            if o.text != "Seleccionar"
        ]

        for comuna in comunas:
            select_comuna.select_by_visible_text(comuna)
            pausa()

            print(f"📍 Procesando → Región: {region} | Provincia: {provincia} | Comuna: {comuna}")

            df = extraer_tabla_presidente(driver)

            if df is None or df.empty:
                print(f"⚠ SIN TABLA → Región: {region} | Provincia: {provincia} | Comuna: {comuna}")
                continue

            df["region"] = region
            df["provincia"] = provincia
            df["comuna"] = comuna

            data_final.append(df)
            #print(f"✔ OK:  → Región: {region} | Provincia: {provincia} | Comuna: {comuna}")

# ============================================================
# GUARDAR
# ============================================================

regiones_norm = REGIONES_INPUT.lower().replace(" ", "_")
nombre_salida = f"presidente_{regiones_norm}.csv"

if len(data_final) == 0:
    print("⚠ No se obtuvo ninguna tabla. No se genera archivo.")
else:
    df_final = pd.concat(data_final, ignore_index=True)
    df_final.to_csv(nombre_salida, index=False)
    print(f"\n✔ FIN - Guardado en: {nombre_salida}")

driver.quit()
