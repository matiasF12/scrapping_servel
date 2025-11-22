import pandas as pd

diputados_por_distrito = {
    8: 8,
    9: 7,
    10: 8,
    11: 6,
    12: 7,
    13: 6,
    14: 6,
    15: 5,
    16: 4,
    5: 7,
    6: 6,
    7: 8
}

def dhondt_distrito(df, distrito):
    # --- Validación
    if distrito not in diputados_por_distrito:
        raise ValueError(f"El distrito {distrito} no está en la tabla de escaños.")

    n_escanos = diputados_por_distrito[distrito]

    # --- 1) Consolidar votos por candidato dentro del distrito
    df_dist = (
        df[df["Distrito"] == distrito]
        .groupby(["pacto", "candidato", "partido"], as_index=False)["votos"]
        .sum()
    )

    # --- 2) Votos totales por pacto
    votos_pacto = df_dist.groupby("pacto")["votos"].sum().reset_index()

    # --- 3) Tabla D'Hondt
    dh = []
    for _, row in votos_pacto.iterrows():
        pacto = row["pacto"]
        votos = row["votos"]

        for div in range(1, n_escanos + 1):
            dh.append({
                "pacto": pacto,
                "division": div,
                "resultado": votos / div
            })

    df_dh = (
        pd.DataFrame(dh)
        .sort_values("resultado", ascending=False)
        .head(n_escanos)
    )

    # --- 4) Escaños por pacto
    escaños_pacto = df_dh.groupby("pacto").size().reset_index(name="escaños")

    # --- 5) Selección de electos
    electos = []

    for _, row in escaños_pacto.iterrows():
        pacto = row["pacto"]
        cupos = row["escaños"]

        cand = (
            df_dist[df_dist["pacto"] == pacto]
            .sort_values("votos", ascending=False)
            .head(cupos)
        )

        electos.append(cand)

    df_electos = pd.concat(electos)

    return df_dh, escaños_pacto, df_electos


# Normalizar tipo de eleccion
def normalizar_tipo_eleccion(tipo_input: str) -> str:
    tipo = tipo_input.strip().lower()

    MAPEO_TIPO = {
        # diputados
        "diputado": "Diputados",
        "diputada": "Diputados",
        "diputados": "Diputados",
        "diputadas": "Diputados",
        "diputa": "Diputados",
        "dip": "Diputados",

        # senadores
        "senador": "Senadores",
        "senadora": "Senadores",
        "senadores": "Senadores",
        "senadoras": "Senadores",
        "sen": "Senadores",

        # presidente
        "presidente": "Presidente",
        "presidenta": "Presidente",
        "presi": "Presidente",
        "pres": "Presidente"
    }

    if tipo not in MAPEO_TIPO:
        raise ValueError(f"Tipo de elección no reconocido: {tipo_input}")

    return MAPEO_TIPO[tipo]


def normalizar_region(nombre_region: str) -> str:
    r = nombre_region.strip().lower()

    MAPEO = {
        # 1
        "arica": "DE ARICA Y PARINACOTA",
        "arica y parinacota": "DE ARICA Y PARINACOTA",
        "parinacota": "DE ARICA Y PARINACOTA",

        # 2
        "tarapaca": "DE TARAPACA",
        "tarapacá": "DE TARAPACA",

        # 3
        "antofagasta": "DE ANTOFAGASTA",

        # 4
        "atacama": "DE ATACAMA",

        # 5
        "coquimbo": "DE COQUIMBO",

        # 6
        "valparaiso": "DE VALPARAISO",
        "valparaíso": "DE VALPARAISO",

        # 7 METROPOLITANA
        "rm": "METROPOLITANA DE SANTIAGO",
        "metropolitana": "METROPOLITANA DE SANTIAGO",
        "santiago": "METROPOLITANA DE SANTIAGO",
        "region metropolitana": "METROPOLITANA DE SANTIAGO",

        # 8 O'HIGGINS
        "ohiggins": "DEL LIBERTADOR GENERAL BERNARDO O'HIGGINS",
        "o'higgins": "DEL LIBERTADOR GENERAL BERNARDO O'HIGGINS",
        "libertador": "DEL LIBERTADOR GENERAL BERNARDO O'HIGGINGS",

        # 9
        "maule": "DEL MAULE",

        # 10 ÑUBLE
        "nuble": "DE ÑUBLE",
        "ñuble": "DE ÑUBLE",

        # 11 BIOBIO
        "biobio": "DE BIOBIO",
        "bío bío": "DE BIOBIO",
        "bio bío": "DE BIOBIO",

        # 12 ARAUCANIA
        "araucania": "DE LA ARAUCANIA",
        "araucanía": "DE LA ARAUCANIA",

        # 13
        "los rios": "DE LOS RIOS",
        "los ríos": "DE LOS RIOS",

        # 14
        "los lagos": "DE LOS LAGOS",

        # 15 AYSÉN
        "aysen": "DE AYSEN DEL GENERAL CARLOS IBAÑEZ DEL CAMPO",
        "aysén": "DE AYSEN DEL GENERAL CARLOS IBAÑEZ DEL CAMPO",
        "aysen del general carlos ibañez del campo": 
            "DE AYSEN DEL GENERAL CARLOS IBAÑEZ DEL CAMPO",

        # 16 MAGALLANES
        "magallanes": "DE MAGALLANES Y DE LA ANTARTICA CHILENA",
        "magallanes y la antartica": "DE MAGALLANES Y DE LA ANTARTICA CHILENA",
        "magallanes y antartica": "DE MAGALLANES Y DE LA ANTARTICA CHILENA",
    }

    # Búsqueda con limpieza extrema
    r2 = (
        r.replace("región", "")
         .replace("region", "")
         .replace("de ", "")
         .strip()
    )

    # 1° intento: clave directa
    if r in MAPEO:
        return MAPEO[r]

    # 2° intento: variante limpiada
    if r2 in MAPEO:
        return MAPEO[r2]

    raise ValueError(f"Región no reconocida: '{nombre_region}'")

def procesar_regiones(REGIONES_INPUT: str):
    txt = REGIONES_INPUT.strip().lower()

    if txt == "todas":
        return ["TODAS"]

    partes = [p.strip() for p in txt.split(",")]
    return [normalizar_region(p) for p in partes]