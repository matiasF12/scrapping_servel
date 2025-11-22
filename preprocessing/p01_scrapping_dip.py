import time
import random
import pandas as pd

from selenium import webdriver
from selenium.webdriver import Chrome
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
from functions.scrapping import pausa, extraer_tabla_js, esperar_actualizacion_tabla, get_selects
# ============================================================
# FUNCIONES
# ============================================================

def pausa():
    time.sleep(random.uniform(0.7, 1.3))

def extraer_tabla_js(driver):
    """
    Extrae la tabla REAL renderizada por Alpine.js dentro de:
    div#filtro_tabla_computo table
    usando JavaScript porque page_source NO sirve.
    """
    rows = driver.execute_script("""
        const tbody = document.querySelector("div#filtro_tabla_computo table tbody");
        if (!tbody) return [];

        let data = [];
        for (const tr of tbody.querySelectorAll("tr")) {
            const tds = [...tr.querySelectorAll("td")].map(td => td.innerText.trim());
            data.push(tds);
        }
        return data;
    """)
    return rows

def get_selects(driver):
    selects = driver.find_elements(By.TAG_NAME, "select")
    return (
        Select(selects[1]),  # Región
        Select(selects[2]),  # Provincia
        Select(selects[3])   # Comuna
    )

def esperar_actualizacion_tabla(driver, ultima_tabla=None, max_espera=6.0, paso=0.3):
    """
    Espera hasta que:
      - la tabla tenga filas, y
      - si se pasa ultima_tabla, que sea distinta a la anterior.

    Si no cambia dentro del tiempo, devuelve lo que haya (aunque sea igual).
    """
    intentos = int(max_espera / paso)
    rows_filtradas = []

    for _ in range(intentos):
        rows = extraer_tabla_js(driver)
        # nos quedamos solo con filas con 5 columnas
        rows_filtradas = [r for r in rows if len(r) == 5]

        if len(rows_filtradas) == 0:
            time.sleep(paso)
            continue

        if ultima_tabla is not None and rows_filtradas == ultima_tabla:
            # tabla igual a la anterior, esperamos un poco más
            time.sleep(paso)
            continue

        # ya hay tabla nueva o primera tabla
        return rows_filtradas

    # si llegamos acá, no cambió (o nunca hubo), devolvemos lo último visto
    return rows_filtradas


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
# CLICK EN DIPUTADOS
# ============================================================

for b in driver.find_elements(By.TAG_NAME, "button"):
    if "Diputado" in b.text:
        b.click()
        break

time.sleep(1)

driver.find_element(By.XPATH, "//button[contains(., 'División Geográfica Chile')]").click()
time.sleep(1.2)

# ============================================================
# SCRAPING
# ============================================================

select_region, select_provincia, select_comuna = get_selects(driver)

regiones = ["METROPOLITANA DE SANTIAGO"]
data_final = []

ultima_tabla = None  # Para detectar tablas repetidas

for region in regiones:

    select_region.select_by_visible_text(region)
    pausa()

    _, select_provincia, _ = get_selects(driver)
    provincias = [o.text for o in select_provincia.options if o.text != "Seleccionar"]

    for provincia in provincias:
        select_provincia.select_by_visible_text(provincia)
        pausa()

        _, _, select_comuna = get_selects(driver)
        comunas = [o.text for o in select_comuna.options if o.text != "Seleccionar"]

        for comuna in comunas:
            select_comuna.select_by_visible_text(comuna)
            pausa()

            # Esperar que la tabla se "actualice" respecto a la última
            rows = esperar_actualizacion_tabla(driver, ultima_tabla=ultima_tabla)

            # si no hay filas, log y seguir
            if len(rows) == 0:
                print("⚠ SIN TABLA ->", comuna)
                continue

            # si es exactamente igual a la anterior, avisamos y NO guardamos
            if ultima_tabla is not None and rows == ultima_tabla:
                print("⚠ TABLA REPETIDA (misma que comuna anterior) ->", comuna)
                continue

            # actualizar última tabla de referencia
            ultima_tabla = rows

            df = pd.DataFrame(rows, columns=[
                "lista_pacto", "partido", "votos", "porcentaje", "candidatos"
            ])

            df["region"] = region
            df["provincia"] = provincia
            df["comuna"] = comuna

            data_final.append(df)

# ============================================================
# GUARDAR
# ============================================================

if len(data_final) == 0:
    print("⚠ No se obtuvo ninguna tabla, data_final está vacío. No se genera CSV.")
else:
    df_final = pd.concat(data_final, ignore_index=True)
    df_final.to_csv("files/datasets/intermedia/diputados_rm_ok.csv", index=False)
    print("✔ FIN - Guardado como diputados_rm_ok.csv")

driver.quit()




