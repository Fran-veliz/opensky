-- KPI: Capacidad vs demanda por aeropuerto/sector (núcleo de ATFM)
-- NOTA: el dataset no incluye capacidades declaradas por aeropuerto/sector
-- (eso normalmente viene de AIP/ASM). Como proxy razonable para un proyecto
-- sin esa fuente, se define la "capacidad" de cada aeropuerto como el
-- percentil 90 de su propia demanda horaria observada en el periodo
-- analizado: una franja que supera ese umbral se interpreta como saturación
-- relativa a su operativa habitual.

WITH demanda_horaria AS (
    SELECT
        ao.codigo_icao AS aeropuerto,
        DATE_TRUNC('hour', f.hora_salida) AS franja_horaria,
        COUNT(*) AS demanda
    FROM fact_vuelo f
    JOIN dim_aeropuerto ao ON ao.aeropuerto_id = f.aeropuerto_origen_id
    WHERE ao.codigo_icao <> 'DESCONOCIDO'
    GROUP BY 1, 2
),
capacidad_proxy AS (
    SELECT
        aeropuerto,
        QUANTILE_CONT(demanda, 0.90) AS capacidad_estimada
    FROM demanda_horaria
    GROUP BY aeropuerto
    HAVING COUNT(*) >= 10
)
SELECT
    d.aeropuerto,
    d.franja_horaria,
    d.demanda,
    c.capacidad_estimada,
    ROUND(d.demanda / c.capacidad_estimada, 2) AS indice_saturacion,
    d.demanda > c.capacidad_estimada AS saturado
FROM demanda_horaria d
JOIN capacidad_proxy c ON c.aeropuerto = d.aeropuerto
ORDER BY indice_saturacion DESC
LIMIT 50;
