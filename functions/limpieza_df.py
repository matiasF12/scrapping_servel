import unicodedata
import re
import numpy as np

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