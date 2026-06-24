# Manual de uso — Proyecto ATFM

## 1. ¿Qué es este proyecto?

Pipeline analítico de **Air Traffic Flow Management (ATFM)** que toma datos
reales de vuelos de [OpenSky Network](https://opensky-network.org/)
(trayectorias, aeropuertos estimados de origen/destino, horarios observados),
los limpia, los carga en un warehouse analítico (DuckDB) con un esquema en
estrella, y expone KPIs operativos mediante notebooks y un dashboard
interactivo.

Ver diagrama de flujo completo: `docs/diagramas/pipeline_flujo.png`.

## 2. Requisitos previos

- Python 3.11 o superior.
- Paquetes listados en `requirements.txt`.

## 3. Instalación

```bash
cd PROYECTO_ATFM
pip install -r requirements.txt
```

## 4. Estructura de carpetas

| Carpeta | Contenido |
|---|---|
| `data/raw/` | Parquet crudo de OpenSky (fuente, no se modifica) |
| `data/staging/` | Datos limpios/enriquecidos (salida de la transformación) |
| `data/processed/` | Warehouse DuckDB (`atfm_warehouse.duckdb`) |
| `src/extraccion/` | Lectura del parquet crudo |
| `src/transformacion/` | Limpieza, control de calidad, métricas de trayectoria |
| `src/load/` | Construcción del esquema y carga al warehouse |
| `sql/ddl/` | Definición de tablas (dimensiones y hechos) |
| `sql/dml/` | Queries de los KPIs |
| `sql/warehause/` | Script consolidado para reconstruir el warehouse manualmente |
| `notebooks/` | Exploración, limpieza y análisis de KPIs en Jupyter |
| `dashboards/` | Dashboard interactivo en Streamlit |
| `docs/` | Documentación, diagramas y manuales |

## 5. Ejecutar el pipeline completo

```bash
python main.py
```

Esto ejecuta en orden: **extracción → transformación → carga**, y genera:

- `data/staging/vuelos_limpios.parquet`
- `data/processed/atfm_warehouse.duckdb`
- `logs/pipeline.log` (registro detallado de cada etapa)

Tiempo aproximado: 3-4 minutos para ~97.000 vuelos (el cálculo de métricas
de trayectoria sobre cada track es el paso más costoso).

## 6. Explorar los datos en notebooks

```bash
jupyter notebook notebooks/
```

- `exploracion.ipynb`: primer vistazo a los datos crudos (esquema, nulos, rangos).
- `limpieza.ipynb`: ejecuta las reglas de limpieza paso a paso y muestra su efecto.
- `analisis_kpis.ipynb`: consulta el warehouse y grafica los 4 KPIs principales.

## 7. Levantar el dashboard interactivo

```bash
streamlit run dashboards/app.py
```

Se abre en `http://localhost:8501` con 4 pestañas:

1. **Tráfico**: top aeropuertos por volumen y rutas más frecuentes.
2. **Congestión y picos**: demanda por hora del día, por aeropuerto+hora y por día de la semana.
3. **Capacidad vs. demanda**: franjas horarias saturadas (ver nota metodológica en la sección 9).
4. **Puntualidad**: retraso relativo de cada vuelo frente al promedio histórico de su ruta.

> Requiere haber corrido `python main.py` al menos una vez antes.

## 8. Consultar el warehouse directamente con SQL

```bash
duckdb data/processed/atfm_warehouse.duckdb
```

Dentro de la consola de DuckDB puedes ejecutar cualquier query de
`sql/dml/*.sql`, o reconstruir el esquema desde cero con:

```bash
duckdb data/processed/atfm_warehouse.duckdb < sql/warehause/00_build_warehouse.sql
```

## 9. Limitaciones conocidas de los datos

- OpenSky no expone **horarios programados**: solo posiciones observadas. Por
  eso la "puntualidad" se mide como desviación frente al promedio histórico
  de la misma ruta, no como retraso oficial contra un horario publicado.
- No hay **capacidades declaradas** por aeropuerto/sector (eso normalmente
  viene de AIP/ASM). Se usa como proxy el percentil 90 de la demanda horaria
  histórica de cada aeropuerto.
- Los aeropuertos de origen/destino son **estimados** por OpenSky a partir de
  la proximidad del track, no confirmados; cada vuelo lleva una etiqueta de
  confianza (`calidad_origen` / `calidad_destino`: alta/media/baja/sin_dato).

## 10. Volver a ejecutar el pipeline con datos nuevos

Basta con colocar el/los nuevos archivos `.parquet` (mismo esquema de
OpenSky) en `data/raw/` y volver a correr `python main.py`. La carga es de
**reemplazo completo**: vacía las tablas del warehouse y las recarga con todo
lo que encuentre en `data/raw/`.
