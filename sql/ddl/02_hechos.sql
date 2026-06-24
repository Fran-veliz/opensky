-- Tabla de hechos: un registro por vuelo observado en OpenSky Network

CREATE SEQUENCE IF NOT EXISTS seq_vuelo_id START 1;

CREATE TABLE IF NOT EXISTS fact_vuelo (
    vuelo_id                BIGINT PRIMARY KEY DEFAULT nextval('seq_vuelo_id'),
    icao24                   VARCHAR NOT NULL,
    callsign                 VARCHAR,
    fecha_id                 BIGINT REFERENCES dim_fecha(fecha_id),
    aeropuerto_origen_id     BIGINT REFERENCES dim_aeropuerto(aeropuerto_id),
    aeropuerto_destino_id    BIGINT REFERENCES dim_aeropuerto(aeropuerto_id),
    hora_salida              TIMESTAMP NOT NULL,
    hora_llegada             TIMESTAMP NOT NULL,
    duracion_minutos         DOUBLE NOT NULL,
    distancia_recorrida_km   DOUBLE,
    distancia_directa_km     DOUBLE,
    altitud_max_m            DOUBLE,
    altitud_promedio_m       DOUBLE,
    num_puntos_track         INTEGER,
    calidad_origen           VARCHAR,
    calidad_destino          VARCHAR,
    archivo_origen           VARCHAR
);

CREATE INDEX IF NOT EXISTS idx_fact_vuelo_fecha ON fact_vuelo(fecha_id);
CREATE INDEX IF NOT EXISTS idx_fact_vuelo_origen ON fact_vuelo(aeropuerto_origen_id);
CREATE INDEX IF NOT EXISTS idx_fact_vuelo_destino ON fact_vuelo(aeropuerto_destino_id);
