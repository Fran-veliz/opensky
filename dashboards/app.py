"""Dashboard interactivo de KPIs ATFM (Streamlit).

Uso:
    streamlit run dashboards/app.py
"""
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1]))

import duckdb
import pandas as pd
import streamlit as st

from src.config.settings import DML_DIR, WAREHOUSE_DB_PATH

st.set_page_config(page_title="ATFM - Panel de KPIs", layout="wide")


@st.cache_resource
def conectar():
    if not WAREHOUSE_DB_PATH.exists():
        st.error(
            f"No se encontró el warehouse en {WAREHOUSE_DB_PATH}. "
            "Ejecuta primero `python main.py` para generarlo."
        )
        st.stop()
    return duckdb.connect(str(WAREHOUSE_DB_PATH), read_only=True)


@st.cache_data
def cargar_sql(nombre_archivo: str, indice: int = 0) -> pd.DataFrame:
    sql = (DML_DIR / nombre_archivo).read_text(encoding="utf-8")
    consultas = [q.strip() for q in sql.split(";") if q.strip()]
    con = conectar()
    return con.execute(consultas[indice]).df()


st.title("Panel de KPIs — ATFM (Air Traffic Flow Management)")
st.caption(
    "Datos de OpenSky Network procesados por el pipeline ETL del proyecto. "
    "Fuente: data/raw → warehouse DuckDB en data/processed/."
)

con = conectar()
total_vuelos, total_aeropuertos, total_dias = con.execute(
    "SELECT (SELECT COUNT(*) FROM fact_vuelo), "
    "(SELECT COUNT(*) FROM dim_aeropuerto), "
    "(SELECT COUNT(*) FROM dim_fecha)"
).fetchone()

col1, col2, col3 = st.columns(3)
col1.metric("Vuelos en el warehouse", f"{total_vuelos:,}")
col2.metric("Aeropuertos observados", f"{total_aeropuertos:,}")
col3.metric("Días cubiertos", total_dias)

tab_trafico, tab_congestion, tab_capacidad, tab_puntualidad = st.tabs(
    ["Tráfico", "Congestión y picos", "Capacidad vs demanda", "Puntualidad"]
)

with tab_trafico:
    st.subheader("Top aeropuertos por volumen de operaciones")
    top_aeropuertos = cargar_sql("kpi_trafico.sql", indice=0)
    st.bar_chart(top_aeropuertos.set_index("codigo_icao")["total_operaciones"].head(15))
    st.dataframe(top_aeropuertos, use_container_width=True)

    st.subheader("Rutas más frecuentes")
    top_rutas = cargar_sql("kpi_trafico.sql", indice=1)
    st.dataframe(top_rutas, use_container_width=True)

with tab_congestion:
    st.subheader("Demanda por hora del día")
    demanda_hora = cargar_sql("kpi_congestion.sql", indice=0)
    st.bar_chart(demanda_hora.set_index("hora_del_dia")["num_despegues"])

    st.subheader("Picos por aeropuerto + hora")
    picos = cargar_sql("kpi_congestion.sql", indice=1)
    st.dataframe(picos, use_container_width=True)

    st.subheader("Demanda por día de la semana")
    dia_semana = cargar_sql("kpi_congestion.sql", indice=2)
    st.bar_chart(dia_semana.set_index("nombre_dia")["num_vuelos"])

with tab_capacidad:
    st.markdown(
        "El dataset no incluye capacidades declaradas por aeropuerto/sector. "
        "Como proxy se usa el **percentil 90** de la demanda horaria histórica "
        "de cada aeropuerto: una franja por encima de ese umbral se interpreta "
        "como saturación relativa a su operativa habitual."
    )
    saturacion = cargar_sql("kpi_capacidad_demanda.sql", indice=0)
    solo_saturados = st.checkbox("Mostrar solo franjas saturadas", value=True)
    if solo_saturados:
        saturacion = saturacion[saturacion["saturado"]]
    st.dataframe(saturacion, use_container_width=True)

with tab_puntualidad:
    st.markdown(
        "OpenSky no expone horarios programados, por lo que el 'retraso' se "
        "mide como desviación de la duración del vuelo frente al promedio "
        "histórico de su misma ruta (proxy de irregularidad, no retraso oficial)."
    )
    retrasos = cargar_sql("kpi_puntualidad.sql", indice=0)
    st.bar_chart(retrasos["clasificacion"].value_counts())
    st.dataframe(
        retrasos.sort_values("retraso_relativo_minutos", key=abs, ascending=False).head(50),
        use_container_width=True,
    )
