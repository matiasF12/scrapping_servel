import pandas as pd
import time
import random
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
from selenium.common.exceptions import TimeoutException

def pausa():
    time.sleep(random.uniform(0.7, 1.3))

def extraer_tabla_js(driver):
    """
    Extrae tabla desde:
    - Diputados/Senadores → div#filtro_tabla_computo
    - Presidente → div#filtro_tabla_presidente
    """
    script = """
        let ids = [
            "filtro_tabla_computo",
            "filtro_tabla_presidente",
            "filtro_tabla_senadores"
        ];

        let tbody = null;

        for (let id of ids) {
            let el = document.querySelector(`div#${id} table tbody`);
            if (el) {
                tbody = el;
                break;
            }
        }

        if (!tbody) return [];

        let data = [];
        for (const tr of tbody.querySelectorAll("tr")) {
            const tds = [...tr.querySelectorAll("td")].map(td => td.innerText.trim());
            data.push(tds);
        }
        return data;
    """
    return driver.execute_script(script)

# def extraer_tabla_js(driver):
#     """
#     Extrae la tabla REAL renderizada por Alpine.js dentro de:
#     div#filtro_tabla_computo table
#     usando JavaScript porque page_source NO sirve.
#     """
#     rows = driver.execute_script("""
#         const tbody = document.querySelector("div#filtro_tabla_computo table tbody");
#         if (!tbody) return [];

#         let data = [];
#         for (const tr of tbody.querySelectorAll("tr")) {
#             const tds = [...tr.querySelectorAll("td")].map(td => td.innerText.trim());
#             data.push(tds);
#         }
#         return data;
#     """)
#     return rows

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


def esperar_select_habilitado(driver, by, selector, timeout=10):
    """
    Espera a que un <select> deje de estar disabled.
    """
    for _ in range(int(timeout / 0.3)):
        try:
            elem = driver.find_element(by, selector)
            # Caso 1: el select ya no está disabled
            if elem.is_enabled():
                # Y tiene opciones
                opts = elem.find_elements(By.TAG_NAME, "option")
                if len(opts) > 1:
                    return elem
        except:
            pass

        time.sleep(0.3)

    raise TimeoutException("El select no se habilitó a tiempo")



def construir_dataframe(rows, tipo, region, provincia, comuna):
    """
    Construye el DataFrame correcto según el tipo de elección.
    
    - Presidente → 4 columnas
    - Senadores → 5 columnas
    - Diputados → 5 columnas
    """

    tipo = tipo.lower()

    if tipo == "presidente":
        rows_limpias = [r[:4] for r in rows]
        # Tabla: candidato, votos, porcentaje, electo
        df = pd.DataFrame(rows_limpias, columns=[
            "candidato", "votos", "porcentaje", "electo"
        ])

    elif tipo == "senadores":
        # Tabla: lista_pacto, votos, porcentaje, electos, candidatos
        # A veces Servel cambia el orden, pero normalmente son 5 columnas
        df = pd.DataFrame(rows, columns=[
            "lista_pacto", "votos", "porcentaje", "electos", "candidatos"
        ])

    else:  # diputados
        df = pd.DataFrame(rows, columns=[
            "lista_pacto", "partido", "votos", "porcentaje", "candidatos"
        ])

    # Agregar metadata de región/provincia/comuna
    df["region"] = region
    df["provincia"] = provincia
    df["comuna"] = comuna

    return df