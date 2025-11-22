import matplotlib.pyplot as plt
import seaborn as sns
import math
import pandas as pd

def graficar_distribucion_comunal(distrito_objetivo, df_final, top_n=10):
    """
    Genera un gráfico de barras apiladas mostrando
    la composición porcentual de votos por comuna
    para los TOP N candidatos de un distrito.
    
    Parámetros:
        distrito_objetivo (int): número del distrito a analizar
        df_final (DataFrame): dataframe con columnas candidato, partido, votos, comuna, Distrito
        top_n (int): cantidad de candidatos a mostrar (default=10)
    """
    
    sns.set(style="whitegrid")
    
    # Filtrar solo el distrito objetivo
    df_dist = df_final[df_final["Distrito"] == distrito_objetivo].copy()
    
    if df_dist.empty:
        print(f"No hay datos para el distrito {distrito_objetivo}.")
        return
    
    # Agregar label candidato + partido
    df_dist["label"] = df_dist["candidato"] + " (" + df_dist["partido"] + ")"
    
    # Agrupar por candidato + comuna
    df_group = (
        df_dist.groupby(["label", "comuna"], as_index=False)["votos"]
        .sum()
    )

    # Total por candidato
    df_total = df_group.groupby("label")["votos"].sum().reset_index()
    df_total = df_total.rename(columns={"votos": "total_candidato"})

    # Ordenar por total y seleccionar top N
    top_labels = df_total.sort_values("total_candidato", ascending=False)["label"].head(top_n)

    # Filtrar solo esos candidatos top N
    df_group = df_group[df_group["label"].isin(top_labels)]

    # Volver a unir totales (solo top)
    df_group = df_group.merge(df_total, on="label", how="left")

    # Porcentaje por comuna
    df_group["pct"] = df_group["votos"] / df_group["total_candidato"]

    # Pivot para gráfico
    df_pivot = df_group.pivot(index="label", columns="comuna", values="pct").fillna(0)

    # Ordenar nuevamente por total dentro del pivot
    df_pivot = df_pivot.loc[top_labels]

    # Graficar
    plt.figure(figsize=(17, 8))
    df_pivot.plot(
        kind="bar",
        stacked=True,
        figsize=(17, 8),
        cmap="tab20",
        edgecolor="black"
    )

    plt.title(
        f"Distrito {distrito_objetivo}: Distribución porcentual de votos por comuna (Top {top_n})",
        fontsize=16
    )
    plt.xlabel("Candidato (Partido)")
    plt.ylabel("Porcentaje de votos")
    plt.legend(title="Comuna", bbox_to_anchor=(1.02, 1), loc="upper left")
    plt.tight_layout()
    plt.show()

def graficar_ranking_distrito(df_final, distrito_objetivo, top_n=10):
    """
    Grafica el ranking de votos por candidato dentro de un distrito.
    
    df_final: dataframe limpio con columnas ['Distrito','candidato','partido','votos']
    distrito_objetivo: número de distrito
    top_n: cantidad de candidatos a mostrar
    """
    sns.set(style="whitegrid")

    # Filtrar distrito
    df_dist = df_final[df_final["Distrito"] == distrito_objetivo].copy()

    if df_dist.empty:
        print(f"No hay datos para el distrito {distrito_objetivo}.")
        return

    # Agrupar votos por candidato
    df_rank = (
        df_dist.groupby(["candidato", "partido"], as_index=False)["votos"]
        .sum()
        .sort_values("votos", ascending=False)
        .head(top_n)
    )

    # Etiqueta combinada
    df_rank["label"] = df_rank["candidato"] + " (" + df_rank["partido"] + ")"

    # Gráfico
    plt.figure(figsize=(12, 7))
    sns.barplot(
        data=df_rank,
        x="votos",
        y="label",
        palette="Blues_r"
    )

    plt.title(f"Distrito {distrito_objetivo} – Ranking de votos por candidato (Top {top_n})",
              fontsize=15)
    plt.xlabel("Votos")
    plt.ylabel("Candidato (Partido)")

    # Etiquetas en las barras
    for i, v in enumerate(df_rank["votos"]):
        plt.text(v + max(df_rank["votos"]) * 0.01, i, f"{v:,}", va='center')

    plt.tight_layout()
    plt.show()

def graficar_distribucion_por_candidato(df_final, distrito_objetivo, top_n=10):
    """
    Genera una grilla donde cada subplot corresponde a un candidato del TOP N
    mostrando los votos por comuna en formato de barras, usando ejes homogéneos
    para facilitar la comparación.
    """
    
    sns.set(style="whitegrid")

    # Filtrar distrito
    df_dist = df_final[df_final["Distrito"] == distrito_objetivo].copy()

    # Votos totales por candidato (TOP N)
    top = (
        df_dist.groupby(["candidato", "partido"], as_index=False)["votos"]
        .sum()
        .sort_values("votos", ascending=False)
        .head(top_n)
    )

    candidatos_top = top["candidato"].tolist()

    df_top = df_dist[df_dist["candidato"].isin(candidatos_top)]

    # 🔥 Obtener máximo global de votos por comuna (para ejes homogéneos)
    max_global = (
        df_top.groupby(["candidato", "comuna"])["votos"]
        .sum()
        .max()
    )

    # Grid size
    cols = 2
    rows = math.ceil(top_n / cols)

    fig, axes = plt.subplots(rows, cols, figsize=(16, 4 * rows))
    axes = axes.flatten()

    for idx, cand in enumerate(candidatos_top):
        ax = axes[idx]

        df_cand = (
            df_top[df_top["candidato"] == cand]
            .groupby("comuna", as_index=False)["votos"]
            .sum()
            .sort_values("votos", ascending=False)
        )

        sns.barplot(
            data=df_cand,
            x="votos",
            y="comuna",
            palette="viridis",
            ax=ax
        )

        partido = top[top["candidato"] == cand]["partido"].iloc[0]

        ax.set_title(f"{cand} ({partido})", fontsize=12)
        ax.set_xlabel("Votos")
        ax.set_ylabel("Comuna")

        # 👉 aplicar mismo eje para todos
        ax.set_xlim(0, max_global * 1.10)

        # etiquetas con números
        for i, v in enumerate(df_cand["votos"]):
            ax.text(
                v + (max_global * 0.02),
                i,
                str(v),
                va='center'
            )

    # Eliminar subplots vacíos
    for j in range(idx+1, len(axes)):
        fig.delaxes(axes[j])

    plt.tight_layout()
    plt.show()

def graficar_distribucion_por_comuna(df_final, distrito_objetivo, top_n=10):
    """
    Genera una grilla donde cada subplot corresponde a una comuna
    mostrando distribución porcentual de votos entre candidatos TOP N.
    """
    
    sns.set(style="whitegrid")

    # Filtrar distrito
    df_dist = df_final[df_final["Distrito"] == distrito_objetivo]

    # Top N candidatos
    top = (
        df_dist.groupby("candidato", as_index=False)["votos"]
        .sum()
        .sort_values("votos", ascending=False)
        .head(top_n)
    )

    top_cands = top["candidato"].tolist()
    df_dist = df_dist[df_dist["candidato"].isin(top_cands)]

    # Comunas ordenadas
    comunas = sorted(df_dist["comuna"].unique())
    n = len(comunas)

    cols = 3
    rows = math.ceil(n / cols)

    fig, axes = plt.subplots(rows, cols, figsize=(18, 4 * rows))
    axes = axes.flatten()

    for idx, comuna in enumerate(comunas):
        ax = axes[idx]

        df_c = df_dist[df_dist["comuna"] == comuna]
        df_c = (
            df_c.groupby("candidato", as_index=False)["votos"]
            .sum()
        )

        total = df_c["votos"].sum()
        df_c["pct"] = df_c["votos"] / total

        sns.barplot(
            data=df_c,
            x="pct",
            y="candidato",
            palette="rocket",
            ax=ax
        )

        ax.set_title(comuna, fontsize=12)
        ax.set_xlabel("% voto")
        ax.set_ylabel("Candidato")

        # etiquetas %
        for i, p in enumerate(df_c["pct"]):
            ax.text(p + 0.01, i, f"{p:.1%}", va='center')

    # eliminar subplots sobrantes
    for j in range(idx+1, len(axes)):
        fig.delaxes(axes[j])

    plt.tight_layout()
    plt.show()



DIPUTADOS_POR_DISTRITO = {
    5: 7, 6: 8, 7: 8,
    8: 8, 9: 7, 10: 8, 11: 6,
    12: 7, 13: 6, 14: 6,
    15: 5, 16: 4
}

from functions.funciones_extras import dhondt_distrito

def grafico_electos_dhondt(df_final, distrito, paleta_pactos):
    """
    Genera un gráfico con los candidatos electos según D'Hondt
    mostrando votos totales, porcentaje y color por pacto.
    """

    # --- Ejecutar DHONDT usando tu función original
    df_dh, escaños_pacto, electos = dhondt_distrito(df_final, distrito)

    # --- Calcular total de votos del distrito
    total_distrito = df_final[df_final["Distrito"] == distrito]["votos"].sum()

    # --- Calcular porcentaje dentro del distrito
    electos = electos.copy()
    electos["pct"] = electos["votos"] / total_distrito * 100

    # --- Etiqueta compuesta
    electos["label"] = electos["candidato"] + " (" + electos["pacto"] + ")"

    # --- Ordenar por votos
    electos = electos.sort_values("votos", ascending=False)

    # --- Construir paleta en base a los pactos presentes
    pactos_presentes = electos["pacto"].unique()
    palette = {p: paleta_pactos.get(p, "#7F8C8D") for p in pactos_presentes}

    # --- Crear gráfico
    plt.figure(figsize=(12, 7))
    
    sns.barplot(
        data=electos,
        x="votos",
        y="label",
        hue="pacto",
        palette=palette,
        dodge=False
    )

    # --- Etiquetas de votos y porcentaje
    for _, row in electos.iterrows():
        plt.text(
            row["votos"] * 1.01,
            row["label"],
            f"{row['votos']:,} votos – {row['pct']:.2f}%",
            va='center',
            fontsize=10
        )

    # --- Títulos y formato
    plt.title(f"Candidatos Electos – Distrito {distrito} (Sistema D'Hondt)", fontsize=15)
    plt.xlabel("Votos")
    plt.ylabel("Candidato")

    plt.legend(title="Pacto", bbox_to_anchor=(1.05, 1), loc="upper left")
    plt.tight_layout()
    plt.show()

    return electos