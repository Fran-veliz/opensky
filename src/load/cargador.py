"""Carga: construye el warehouse en DuckDB y carga dimensiones + hechos."""
import duckdb
import pandas as pd

from src.config.settings import DDL_DIR, WAREHOUSE_DB_PATH
from src.utils.logger import get_logger

logger = get_logger(__name__)


def _ejecutar_ddl(con: duckdb.DuckDBPyConnection) -> None:
    for archivo_sql in sorted(DDL_DIR.glob("*.sql")):
        logger.info("Ejecutando DDL %s", archivo_sql.name)
        con.execute(archivo_sql.read_text(encoding="utf-8"))


def _construir_dim_fecha(df: pd.DataFrame) -> pd.DataFrame:
    fechas = pd.DataFrame({"fecha": pd.to_datetime(df["fecha_vuelo"].unique())})
    fechas["anio"] = fechas["fecha"].dt.year
    fechas["mes"] = fechas["fecha"].dt.month
    fechas["dia"] = fechas["fecha"].dt.day
    fechas["dia_semana"] = fechas["fecha"].dt.dayofweek
    fechas["nombre_dia"] = fechas["fecha"].dt.day_name(locale="es_ES") if _locale_es_disponible() else fechas["fecha"].dt.day_name()
    fechas["es_fin_de_semana"] = fechas["dia_semana"] >= 5
    fechas["fecha"] = fechas["fecha"].dt.date
    return fechas


def _locale_es_disponible() -> bool:
    try:
        pd.Timestamp.now().day_name(locale="es_ES")
        return True
    except Exception:
        return False


def _construir_dim_aeropuerto(df: pd.DataFrame) -> pd.DataFrame:
    origenes = df[["aeropuerto_origen", "lat_origen", "lon_origen"]].rename(
        columns={"aeropuerto_origen": "codigo_icao", "lat_origen": "lat", "lon_origen": "lon"}
    )
    destinos = df[["aeropuerto_destino", "lat_destino", "lon_destino"]].rename(
        columns={"aeropuerto_destino": "codigo_icao", "lat_destino": "lat", "lon_destino": "lon"}
    )
    todos = pd.concat([origenes, destinos], ignore_index=True)

    aeropuertos = (
        todos.groupby("codigo_icao")
        .agg(
            latitud_aprox=("lat", "mean"),
            longitud_aprox=("lon", "mean"),
            num_vuelos_observados=("codigo_icao", "size"),
        )
        .reset_index()
    )
    return aeropuertos


def cargar_warehouse(df: pd.DataFrame) -> None:
    con = duckdb.connect(str(WAREHOUSE_DB_PATH))
    try:
        _ejecutar_ddl(con)

        logger.info("Recarga completa: vaciando tablas existentes")
        con.execute("DELETE FROM fact_vuelo")
        con.execute("DELETE FROM dim_aeropuerto")
        con.execute("DELETE FROM dim_fecha")

        dim_fecha = _construir_dim_fecha(df)
        con.register("dim_fecha_df", dim_fecha)
        con.execute(
            "INSERT INTO dim_fecha (fecha, anio, mes, dia, dia_semana, nombre_dia, es_fin_de_semana) "
            "SELECT fecha, anio, mes, dia, dia_semana, nombre_dia, es_fin_de_semana FROM dim_fecha_df"
        )
        logger.info("dim_fecha cargada: %d filas", len(dim_fecha))

        dim_aeropuerto = _construir_dim_aeropuerto(df)
        con.register("dim_aeropuerto_df", dim_aeropuerto)
        con.execute(
            "INSERT INTO dim_aeropuerto (codigo_icao, latitud_aprox, longitud_aprox, num_vuelos_observados) "
            "SELECT codigo_icao, latitud_aprox, longitud_aprox, num_vuelos_observados FROM dim_aeropuerto_df"
        )
        logger.info("dim_aeropuerto cargada: %d filas", len(dim_aeropuerto))

        con.register("staging_vuelos", df)
        con.execute(
            """
            INSERT INTO fact_vuelo (
                icao24, callsign, fecha_id, aeropuerto_origen_id, aeropuerto_destino_id,
                hora_salida, hora_llegada, duracion_minutos, distancia_recorrida_km,
                distancia_directa_km, altitud_max_m, altitud_promedio_m, num_puntos_track,
                calidad_origen, calidad_destino, archivo_origen
            )
            SELECT
                s.icao24, s.callsign, f.fecha_id, ao.aeropuerto_id, ad.aeropuerto_id,
                s.hora_salida, s.hora_llegada, s.duracion_minutos, s.distancia_recorrida_km,
                s.distancia_directa_km, s.altitud_max_m, s.altitud_promedio_m, s.num_puntos_track,
                s.calidad_origen, s.calidad_destino, s.archivo_origen
            FROM staging_vuelos s
            LEFT JOIN dim_fecha f ON f.fecha = s.fecha_vuelo
            LEFT JOIN dim_aeropuerto ao ON ao.codigo_icao = s.aeropuerto_origen
            LEFT JOIN dim_aeropuerto ad ON ad.codigo_icao = s.aeropuerto_destino
            """
        )
        total = con.execute("SELECT COUNT(*) FROM fact_vuelo").fetchone()[0]
        logger.info("fact_vuelo cargada: %d filas", total)
    finally:
        con.close()
