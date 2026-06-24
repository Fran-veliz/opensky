-- KPI: Congestión y picos de tráfico (franjas horarias de mayor saturación)

-- Demanda por hora del día (todas las fechas agregadas) a nivel global
SELECT
    EXTRACT(HOUR FROM hora_salida) AS hora_del_dia,
    COUNT(*) AS num_despegues
FROM fact_vuelo
GROUP BY 1
ORDER BY 1;

-- Top combinaciones aeropuerto + hora con mayor demanda (picos de congestión)
SELECT
    ao.codigo_icao AS aeropuerto,
    EXTRACT(HOUR FROM f.hora_salida) AS hora_del_dia,
    COUNT(*) AS num_despegues
FROM fact_vuelo f
JOIN dim_aeropuerto ao ON ao.aeropuerto_id = f.aeropuerto_origen_id
WHERE ao.codigo_icao <> 'DESCONOCIDO'
GROUP BY 1, 2
ORDER BY num_despegues DESC
LIMIT 25;

-- Demanda por día de la semana
SELECT
    df.nombre_dia,
    df.dia_semana,
    df.es_fin_de_semana,
    COUNT(*) AS num_vuelos
FROM fact_vuelo f
JOIN dim_fecha df ON df.fecha_id = f.fecha_id
GROUP BY 1, 2, 3
ORDER BY df.dia_semana;
