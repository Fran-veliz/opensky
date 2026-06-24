-- Dimensiones del warehouse ATFM (esquema en estrella)

CREATE SEQUENCE IF NOT EXISTS seq_aeropuerto_id START 1;
CREATE SEQUENCE IF NOT EXISTS seq_fecha_id START 1;

CREATE TABLE IF NOT EXISTS dim_aeropuerto (
    aeropuerto_id        BIGINT PRIMARY KEY DEFAULT nextval('seq_aeropuerto_id'),
    codigo_icao          VARCHAR UNIQUE NOT NULL,
    latitud_aprox        DOUBLE,
    longitud_aprox       DOUBLE,
    num_vuelos_observados BIGINT DEFAULT 0
);

CREATE TABLE IF NOT EXISTS dim_fecha (
    fecha_id        BIGINT PRIMARY KEY DEFAULT nextval('seq_fecha_id'),
    fecha           DATE UNIQUE NOT NULL,
    anio            INTEGER NOT NULL,
    mes             INTEGER NOT NULL,
    dia             INTEGER NOT NULL,
    dia_semana      INTEGER NOT NULL, -- 0=lunes ... 6=domingo
    nombre_dia      VARCHAR NOT NULL,
    es_fin_de_semana BOOLEAN NOT NULL
);
