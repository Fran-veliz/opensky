"""Extracción: lectura de los archivos parquet crudos (formato OpenSky Network)."""
import pandas as pd

from src.config.settings import RAW_DIR, RAW_PARQUET_GLOB
from src.utils.logger import get_logger

logger = get_logger(__name__)

COLUMNAS_NECESARIAS = [
    "icao24",
    "firstSeen",
    "estDepartureAirport",
    "lastSeen",
    "estArrivalAirport",
    "callsign",
    "track",
    "estDepartureAirportHorizDistance",
    "estDepartureAirportVertDistance",
    "estArrivalAirportHorizDistance",
    "estArrivalAirportVertDistance",
    "departureAirportCandidatesCount",
    "arrivalAirportCandidatesCount",
]


def extraer_vuelos_raw() -> pd.DataFrame:
    """Lee todos los archivos parquet crudos en data/raw y los concatena."""
    archivos = sorted(RAW_DIR.glob(RAW_PARQUET_GLOB))
    if not archivos:
        raise FileNotFoundError(f"No se encontraron archivos parquet en {RAW_DIR}")

    logger.info("Encontrados %d archivo(s) parquet en %s", len(archivos), RAW_DIR)

    dataframes = []
    for archivo in archivos:
        logger.info("Leyendo %s", archivo.name)
        df = pd.read_parquet(archivo, columns=COLUMNAS_NECESARIAS)
        df["archivo_origen"] = archivo.name
        dataframes.append(df)

    df_total = pd.concat(dataframes, ignore_index=True)
    logger.info("Extracción completada: %d filas, %d columnas", *df_total.shape)
    return df_total
