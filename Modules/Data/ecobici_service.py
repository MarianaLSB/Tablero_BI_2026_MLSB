import requests
import pandas as pd
import numpy as np

# ── URLs base ──────────────────────────────────────────────────────────────────
GBFS_ROOT              = "https://gbfs.mex.lyftbikes.com/gbfs/gbfs.json"
URL_STATION_INFO       = "https://gbfs.mex.lyftbikes.com/gbfs/es/station_information.json"
URL_STATION_STATUS     = "https://gbfs.mex.lyftbikes.com/gbfs/es/station_status.json"

# Columnas que nos interesan de cada endpoint
COLS_INFO   = ["station_id", "name", "lat", "lon", "capacity"]
COLS_STATUS = ["station_id", "num_bikes_available", "num_bikes_disabled",
               "num_docks_available", "num_docks_disabled", "is_renting"]


# ── Helpers ────────────────────────────────────────────────────────────────────

def _fetch_json(url: str) -> dict:
    """
    Hace GET a `url` y regresa el JSON parseado.
    Lanza un error claro si la petición falla.
    """
    response = requests.get(url, timeout=15)
    response.raise_for_status()          # lanza HTTPError si no es 200
    return response.json()


# ── Funciones principales ──────────────────────────────────────────────────────

def get_feed_urls(lang: str = "es") -> dict:
    """
    Consulta el índice GBFS y regresa un diccionario
    {nombre_feed: url} para el idioma indicado.

    Parámetros
    ----------
    lang : str
        Idioma del feed. Por defecto "es" (español).

    Retorna
    -------
    dict  {nombre: url}
    """
    data = _fetch_json(GBFS_ROOT)
    feeds = data["data"][lang]["feeds"]
    return {feed["name"]: feed["url"] for feed in feeds}


def load_station_info() -> pd.DataFrame:
    """
    Carga la información estática de las ciclo-estaciones
    (ubicación, capacidad, id y nombre).

    Retorna
    -------
    pd.DataFrame con columnas: station_id, name, lat, lon, capacity
    """
    data  = _fetch_json(URL_STATION_INFO)
    df    = pd.DataFrame(data["data"]["stations"])

    # Nos quedamos sólo con las columnas de interés
    df = df[COLS_INFO].copy()

    # Tipos correctos
    df["station_id"] = df["station_id"].astype(str)
    df["capacity"]   = pd.to_numeric(df["capacity"],   errors="coerce")
    df["lat"]        = pd.to_numeric(df["lat"],        errors="coerce")
    df["lon"]        = pd.to_numeric(df["lon"],        errors="coerce")

    return df


def load_station_status() -> pd.DataFrame:
    """
    Carga el estado en tiempo real de las ciclo-estaciones
    (bicicletas y docks disponibles/deshabilitados).

    Retorna
    -------
    pd.DataFrame con columnas: station_id, num_bikes_available,
    num_bikes_disabled, num_docks_available, num_docks_disabled, is_renting
    """
    data   = _fetch_json(URL_STATION_STATUS)
    df     = pd.DataFrame(data["data"]["stations"])

    df = df[COLS_STATUS].copy()

    df["station_id"] = df["station_id"].astype(str)
    for col in COLS_STATUS[1:-1]:          # columnas numéricas (todo menos station_id e is_renting)
        df[col] = pd.to_numeric(df[col], errors="coerce")

    return df


def load_ecobici_data() -> pd.DataFrame:
    """
    Función principal: carga y combina información + estado
    de todas las ciclo-estaciones en un único DataFrame.

    Valida que ambos conjuntos de datos tengan las mismas
    estaciones antes de concatenar.

    Retorna
    -------
    pd.DataFrame combinado con columnas de info y status.
    """
    print("📡 Cargando información de estaciones...")
    df_info   = load_station_info()

    print("🔄 Cargando estado en tiempo real...")
    df_status = load_station_status()

    # ── Validación de consistencia ──────────────────────────────────────────
    ids_info   = set(df_info["station_id"])
    ids_status = set(df_status["station_id"])

    solo_info   = ids_info   - ids_status
    solo_status = ids_status - ids_info

    if solo_info or solo_status:
        print(f"⚠️  Estaciones sólo en info:   {len(solo_info)}")
        print(f"⚠️  Estaciones sólo en status: {len(solo_status)}")
        print("   Se hará un inner join para conservar sólo las coincidentes.")
        df = df_info.merge(
            df_status.drop(columns="station_id"),   # evitar duplicado de columna
            left_index=False,
            right_index=False,
            how="inner",
            left_on="station_id",
            right_on="station_id"
        )
    else:
        # Mismo orden garantizado → concat directo (igual que en el notebook)
        df_info   = df_info.sort_values("station_id").reset_index(drop=True)
        df_status = df_status.sort_values("station_id").reset_index(drop=True)
        df        = pd.concat(
            [df_info, df_status.drop(columns="station_id")],
            axis=1
        )

    # ── Feature engineering básico ─────────────────────────────────────────
    df["pct_bikes_available"] = (
        df["num_bikes_available"] / df["capacity"].replace(0, np.nan) * 100
    ).round(1)

    df["pct_docks_available"] = (
        df["num_docks_available"] / df["capacity"].replace(0, np.nan) * 100
    ).round(1)

    print(f"✅ Datos listos: {df.shape[0]} estaciones × {df.shape[1]} columnas")
    return df


# ── Diagnóstico rápido ─────────────────────────────────────────────────────────

def diagnostico(df: pd.DataFrame) -> None:
    """
    Imprime un resumen rápido del DataFrame cargado:
    shape, nulos, estadísticas de disponibilidad.
    """
    print("=" * 50)
    print(f"Shape        : {df.shape}")
    print(f"Estaciones   : {df['station_id'].nunique()}")
    print("-" * 50)
    print("Valores nulos por columna:")
    print(df.isna().sum()[df.isna().sum() > 0].to_string() or "  Ninguno ✅")
    print("-" * 50)
    print("Estaciones activas (is_renting=1) :",
          df["is_renting"].sum(), "/", len(df))
    print("Bicicletas disponibles (total)    :",
          int(df["num_bikes_available"].sum()))
    print("Docks disponibles (total)         :",
          int(df["num_docks_available"].sum()))
    print("=" * 50)


# ── Uso directo del módulo ─────────────────────────────────────────────────────
if __name__ == "__main__":
    df = load_ecobici_data()
    diagnostico(df)
    print(df.head())
