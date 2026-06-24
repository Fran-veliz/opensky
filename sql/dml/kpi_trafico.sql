-- KPI: Tráfico por aeropuerto y por ruta

-- Top aeropuertos por volumen total (salidas + llegadas)
SELECT
    codigo_icao,
    SUM(salidas) AS salidas,
    SUM(llegadas) AS llegadas,
    SUM(salidas) + SUM(llegadas) AS total_operaciones
FROM (
    SELECT ao.codigo_icao, COUNT(*) AS salidas, 0 AS llegadas
    FROM fact_vuelo f JOIN dim_aeropuerto ao ON ao.aeropuerto_id = f.aeropuerto_origen_id
    WHERE ao.codigo_icao <> 'DESCONOCIDO'
    GROUP BY ao.codigo_icao
    UNION ALL
    SELECT ad.codigo_icao, 0 AS salidas, COUNT(*) AS llegadas
    FROM fact_vuelo f JOIN dim_aeropuerto ad ON ad.aeropuerto_id = f.aeropuerto_destino_id
    WHERE ad.codigo_icao <> 'DESCONOCIDO'
    GROUP BY ad.codigo_icao
) t
GROUP BY codigo_icao
ORDER BY total_operaciones DESC
LIMIT 25;

-- Rutas (origen-destino) más frecuentes
SELECT
    ao.codigo_icao AS origen,
    ad.codigo_icao AS destino,
    COUNT(*) AS num_vuelos,
    ROUND(AVG(f.duracion_minutos), 1) AS duracion_promedio_min,
    ROUND(AVG(f.distancia_recorrida_km), 1) AS distancia_promedio_km
FROM fact_vuelo f
JOIN dim_aeropuerto ao ON ao.aeropuerto_id = f.aeropuerto_origen_id
JOIN dim_aeropuerto ad ON ad.aeropuerto_id = f.aeropuerto_destino_id
WHERE ao.codigo_icao <> 'DESCONOCIDO' AND ad.codigo_icao <> 'DESCONOCIDO'
GROUP BY 1, 2
ORDER BY num_vuelos DESC
LIMIT 25;
