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