"""Transformación: limpieza, control de calidad y enriquecimiento de los vuelos."""
import pandas as pd

from src.config.settings import CONFIANZA_DISTANCIA_HORIZ_MAX_M, STAGING_PARQUET_PATH
from src.utils.geo import metricas_track, punto_extremo
from src.utils.logger import get_logger

logger = get_logger(__name__)

AEROPUERTO_DESCONOCIDO = "DESCONOCIDO"


def _calidad_aeropuerto(horiz_distance: float, num_candidatos: float) -> str:
    """Clasifica la confianza de un aeropuerto estimado por OpenSky."""
    if pd.isna(horiz_distance):
        return "sin_dato"
    if horiz_distance <= CONFIANZA_DISTANCIA_HORIZ_MAX_M and num_candidatos <= 1:
        return "alta"
    if horiz_distance <= CONFIANZA_DISTANCIA_HORIZ_MAX_M * 3:
        return "media"
    return "baja"


def limpiar_vuelos(df: pd.DataFrame) -> pd.DataFrame:
    filas_iniciales = len(df)

    df = df.dropna(subset=["firstSeen", "lastSeen", "icao24"]).copy()
    df = df.drop_duplicates(subset=["icao24", "firstSeen", "lastSeen"])

    df["duracion_minutos"] = (df["lastSeen"] - df["firstSeen"]) / 60.0
    df = df[df["duracion_minutos"] > 0]

    eliminadas = filas_iniciales - len(df)
    logger.info(
        "Limpieza: %d filas eliminadas (nulas/duplicadas/duración inválida) de %d",
        eliminadas,
        filas_iniciales,
    )
    return df


def enriquecer_vuelos(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()

    df["hora_salida"] = pd.to_datetime(df["firstSeen"], unit="s", utc=True)
    df["hora_llegada"] = pd.to_datetime(df["lastSeen"], unit="s", utc=True)
    df["fecha_vuelo"] = df["hora_salida"].dt.date

    df["aeropuerto_origen"] = df["estDepartureAirport"].fillna(AEROPUERTO_DESCONOCIDO)
    df["aeropuerto_destino"] = df["estArrivalAirport"].fillna(AEROPUERTO_DESCONOCIDO)

    df["calidad_origen"] = df.apply(
        lambda r: _calidad_aeropuerto(
            r["estDepartureAirportHorizDistance"], r["departureAirportCandidatesCount"]
        ),
        axis=1,
    )
    df["calidad_destino"] = df.apply(
        lambda r: _calidad_aeropuerto(
            r["estArrivalAirportHorizDistance"], r["arrivalAirportCandidatesCount"]
        ),
        axis=1,
    )

    logger.info("Calculando métricas de trayectoria a partir del track (puede tardar)...")
    metricas = df["track"].apply(metricas_track).apply(pd.Series)
    df = pd.concat([df.reset_index(drop=True), metricas.reset_index(drop=True)], axis=1)

    puntos_origen = df["track"].apply(lambda t: punto_extremo(t, "primero"))
    puntos_destino = df["track"].apply(lambda t: punto_extremo(t, "ultimo"))
    df["lat_origen"] = puntos_origen.apply(lambda p: p[0])
    df["lon_origen"] = puntos_origen.apply(lambda p: p[1])
    df["lat_destino"] = puntos_destino.apply(lambda p: p[0])
    df["lon_destino"] = puntos_destino.apply(lambda p: p[1])

    df = df.drop(columns=["track"])
    return df


def transformar(df: pd.DataFrame) -> pd.DataFrame:
    df = limpiar_vuelos(df)
    df = enriquecer_vuelos(df)
    logger.info("Transformación completada: %d filas listas para staging", len(df))
    return df


def guardar_staging(df: pd.DataFrame) -> None:
    df.to_parquet(STAGING_PARQUET_PATH, index=False)
    logger.info("Staging guardado en %s (%d filas)", STAGING_PARQUET_PATH, len(df))
