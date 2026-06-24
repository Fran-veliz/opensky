"""Logger compartido por todas las etapas del pipeline."""
import logging
import sys

from src.config.settings import LOGS_DIR


def get_logger(nombre: str) -> logging.Logger:
    logger = logging.getLogger(nombre)
    if logger.handlers:
        return logger

    logger.setLevel(logging.INFO)
    formato = logging.Formatter(
        "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    consola = logging.StreamHandler(sys.stdout)
    consola.setFormatter(formato)
    logger.addHandler(consola)

    archivo = logging.FileHandler(LOGS_DIR / "pipeline.log", encoding="utf-8")
    archivo.setFormatter(formato)
    logger.addHandler(archivo)

    return logger
