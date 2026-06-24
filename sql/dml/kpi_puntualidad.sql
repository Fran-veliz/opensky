-- KPI: Puntualidad y retrasos
-- NOTA: OpenSky no expone horarios programados (schedule), solo posiciones
-- observadas. Por eso el "retraso" se modela como RETRASO RELATIVO: cuánto
-- se desvía la duración de un vuelo respecto al promedio histórico de su
-- misma ruta (origen-destino). Es un proxy razonable de irregularidad,
-- no un retraso oficial contra horario publicado.

WITH duracion_por_ruta AS (
    SELECT
        ao.codigo_icao AS origen,
        ad.codigo_icao AS destino,
        AVG(f.duracion_minutos) AS duracion_promedio_ruta,
        STDDEV_POP(f.duracion_minutos) AS desviacion_ruta,
        COUNT(*) AS num_vuelos_ruta
    FROM fact_vuelo f
    JOIN dim_aeropuerto ao ON ao.aeropuerto_id = f.aeropuerto_origen_id
    JOIN dim_aeropuerto ad ON ad.aeropuerto_id = f.aeropuerto_destino_id
    WHERE ao.codigo_icao <> 'DESCONOCIDO' AND ad.codigo_icao <> 'DESCONOCIDO'
    GROUP BY 1, 2
    HAVING COUNT(*) >= 5
)
SELECT
    ao.codigo_icao AS origen,
    ad.codigo_icao AS destino,
    f.icao24,
    f.callsign,
    f.hora_salida,
    f.duracion_minutos,
    d.duracion_promedio_ruta,
    f.duracion_minutos - d.duracion_promedio_ruta AS retraso_relativo_minutos,
    CASE
        WHEN f.duracion_minutos - d.duracion_promedio_ruta > d.desviacion_ruta THEN 'mas_lento_que_lo_usual'
        WHEN d.duracion_promedio_ruta - f.duracion_minutos > d.desviacion_ruta THEN 'mas_rapido_que_lo_usual'
        ELSE 'dentro_de_lo_normal'
    END AS clasificacion
FROM fact_vuelo f
JOIN dim_aeropuerto ao ON ao.aeropuerto_id = f.aeropuerto_origen_id
JOIN dim_aeropuerto ad ON ad.aeropuerto_id = f.aeropuerto_destino_id
JOIN duracion_por_ruta d ON d.origen = ao.codigo_icao AND d.destino = ad.codigo_icao
ORDER BY ABS(retraso_relativo_minutos) DESC;
