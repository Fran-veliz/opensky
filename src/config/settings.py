"""Configuración centralizada de rutas y parámetros del pipeline ATFM."""
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[2]

DATA_DIR = BASE_DIR / "data"
RAW_DIR = DATA_DIR / "raw"
STAGING_DIR = DATA_DIR / "staging"
PROCESSED_DIR = DATA_DIR / "processed"
BACKUPS_DIR = DATA_DIR / "backups"

SQL_DIR = BASE_DIR / "sql"
DDL_DIR = SQL_DIR / "ddl"
DML_DIR = SQL_DIR / "dml"

LOGS_DIR = BASE_DIR / "logs"

RAW_PARQUET_GLOB = "*.snappy.parquet"

WAREHOUSE_DB_PATH = PROCESSED_DIR / "atfm_warehouse.duckdb"
STAGING_PARQUET_PATH = STAGING_DIR / "vuelos_limpios.parquet"

# Umbral de confianza para aceptar un aeropuerto estimado: distancia horizontal
# (metros) entre la última posición conocida del track y el aeropuerto candidato.
CONFIANZA_DISTANCIA_HORIZ_MAX_M = 5000

for _dir in (STAGING_DIR, PROCESSED_DIR, BACKUPS_DIR, LOGS_DIR):
    _dir.mkdir(parents=True, exist_ok=True)
