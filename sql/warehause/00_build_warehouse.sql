-- Script consolidado para construir el warehouse ATFM manualmente, p. ej.:
--   duckdb data/processed/atfm_warehouse.duckdb < sql/warehause/00_build_warehouse.sql
-- El pipeline (src/load/cargador.py) ejecuta el mismo contenido de forma programática.

.read sql/ddl/01_dimensiones.sql
.read sql/ddl/02_hechos.sql
