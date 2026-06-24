"""Orquestador del pipeline ATFM: extracción -> transformación -> carga."""
import time

from src.extraccion.extractor import extraer_vuelos_raw
from src.load.cargador import cargar_warehouse
from src.transformacion.transformador import guardar_staging, transformar
from src.utils.logger import get_logger

logger = get_logger(__name__)


def main() -> None:
    inicio = time.time()
    logger.info("=== Iniciando pipeline ATFM ===")

    df_raw = extraer_vuelos_raw()
    df_limpio = transformar(df_raw)
    guardar_staging(df_limpio)
    cargar_warehouse(df_limpio)

    logger.info("=== Pipeline finalizado en %.1f s ===", time.time() - inicio)


if __name__ == "__main__":
    main()
