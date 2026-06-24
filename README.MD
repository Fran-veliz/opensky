# PROYECTO_ATFM

Pipeline analítico de **Air Traffic Flow Management (ATFM)** sobre datos reales de vuelos
de [OpenSky Network](https://opensky-network.org/) (`data/raw/*.parquet`): trayectorias,
aeropuertos estimados de origen/destino y horarios observados.

## Arquitectura

```
data/raw          -> parquet crudo (export de OpenSky)
data/staging       -> parquet limpio/enriquecido (salida de transformación)
data/processed     -> warehouse DuckDB (atfm_warehouse.duckdb)
src/extraccion     -> lectura del parquet crudo
src/transformacion -> limpieza, control de calidad, métricas de trayectoria (haversine)
src/load           -> construcción del esquema en estrella y carga al warehouse
sql/ddl            -> definición de dimensiones y tabla de hechos
sql/dml            -> queries de KPIs
sql/warehause      -> script consolidado para reconstruir el warehouse manualmente
notebooks          -> exploración, limpieza y análisis de KPIs en Jupyter
```

### Modelo de datos (esquema en estrella)

- `dim_fecha`: calendario por día (año, mes, día, día de semana, fin de semana).
- `dim_aeropuerto`: aeropuertos (código ICAO estimado) con posición aproximada
  derivada de las trayectorias observadas.
- `fact_vuelo`: un registro por vuelo, con duración, distancia recorrida vs.
  distancia directa, altitud y nivel de confianza del aeropuerto estimado.

## Uso

```bash
pip install -r requirements.txt
python main.py
```

Esto genera `data/staging/vuelos_limpios.parquet` y el warehouse
`data/processed/atfm_warehouse.duckdb`, listo para consultarse con las queries
de `sql/dml/` o desde los notebooks.

## KPIs disponibles (`sql/dml/`)

- **Puntualidad/retrasos** (`kpi_puntualidad.sql`): como OpenSky no expone horarios
  programados, se mide el *retraso relativo* de cada vuelo frente a la duración
  promedio histórica de su misma ruta.
- **Tráfico** (`kpi_trafico.sql`): volumen de operaciones por aeropuerto y rutas
  más frecuentes.
- **Congestión y picos** (`kpi_congestion.sql`): demanda por hora del día, por
  aeropuerto+hora y por día de la semana.
- **Capacidad vs. demanda** (`kpi_capacidad_demanda.sql`): al no contar con
  capacidades declaradas por aeropuerto/sector, se usa como proxy el percentil 90
  de la demanda horaria histórica de cada aeropuerto para detectar franjas
  saturadas.

## Notebooks

- `exploracion.ipynb`: primer vistazo a los datos crudos.
- `limpieza.ipynb`: validación de las reglas de limpieza aplicadas en `src/transformacion`.
- `analisis_kpis.ipynb`: visualización de los KPIs anteriores contra el warehouse DuckDB.
