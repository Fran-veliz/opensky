# Información de los datos — Proyecto ATFM

## 1. Fuente

[OpenSky Network](https://opensky-network.org/), red colaborativa de
receptores ADS-B que registra posiciones reales de aeronaves a nivel mundial.
El export usado (`data/raw/*.parquet`) corresponde a vuelos reconstruidos a
partir de esas posiciones (formato "flights" de OpenSky).

## 2. Alcance del archivo actual

- **97.217 vuelos** registrados.
- Periodo: **2026-02-28 a 2026-03-01** (aprox. 2 días).
- **5.339** aeropuertos de origen distintos y **6.811** de destino (códigos ICAO estimados).

## 3. Columnas del parquet crudo

| Columna | Tipo | Descripción |
|---|---|---|
| `icao24` | string | Identificador hexadecimal único del transpondedor de la aeronave |
| `firstSeen` / `lastSeen` | int32 (epoch) | Primer/último instante en que se vio la aeronave en este vuelo |
| `callsign` | string | Indicativo de vuelo (puede coincidir con matrícula en aviación general) |
| `estDepartureAirport` / `estArrivalAirport` | string | Aeropuerto de origen/destino **estimado** por proximidad del track |
| `estDepartureAirportHorizDistance` / `VertDistance` | int32 | Distancia horizontal/vertical (m) entre el track y el aeropuerto estimado de origen |
| `estArrivalAirportHorizDistance` / `VertDistance` | int32 | Igual que arriba, para el aeropuerto de destino |
| `departureAirportCandidatesCount` / `arrivalAirportCandidatesCount` | int32 | Nº de aeropuertos candidatos considerados (más candidatos = más ambigüedad) |
| `track` | list\<struct\> | Secuencia de puntos `{time, latitude, longitude, altitude, heading, onGround}` |
| `airportOfDeparture` / `airportOfDestination` | string | Aeropuerto **confirmado** (en este export, 100% nulo: no disponible) |
| `takeoffLandingInfo` | struct | Horarios/coordenadas exactas de despegue-aterrizaje (en este export, 100% nulo) |
| `serials` | list\<int32\> | IDs de los receptores ADS-B que captaron la aeronave |
| `otherDepartureAirportCandidates` / `otherArrivalAirportCandidates` | list\<struct\> | Aeropuertos candidatos alternativos descartados |

## 4. Calidad de los datos observada

- `firstSeen`: 363 valores nulos (0.4%) → se descartan en la limpieza.
- `estDepartureAirport`: 23.853 nulos (24.5%) → vuelos sin aeropuerto de origen estimable.
- `estArrivalAirport`: 14.525 nulos (14.9%) → vuelos sin aeropuerto de destino estimable.
- `airportOfDeparture`, `airportOfDestination`, `takeoffLandingInfo`: 100% nulos en este export, no se usan.
- Longitud del `track` por vuelo: mediana 141 puntos, máximo 2.400 puntos.

Los nulos de aeropuerto **no se descartan**: se etiquetan como `DESCONOCIDO`
para no perder volumen de tráfico real, y se conserva el campo
`calidad_origen`/`calidad_destino` para filtrarlos en los análisis si es
necesario.

## 5. Columnas derivadas que agrega el pipeline

Calculadas en `src/transformacion/transformador.py` a partir del `track`:

- `duracion_minutos`: `(lastSeen - firstSeen) / 60`.
- `distancia_recorrida_km`: suma de distancias ortodrómicas (haversine) entre puntos consecutivos del track.
- `distancia_directa_km`: distancia ortodrómica entre el primer y el último punto del track.
- `altitud_max_m` / `altitud_promedio_m`: estadísticos de altitud sobre los puntos del track.
- `calidad_origen` / `calidad_destino`: clasificación `alta` / `media` / `baja` / `sin_dato` según la distancia horizontal al aeropuerto estimado y el número de candidatos.

## 6. Modelo de datos en el warehouse

Ver diagrama: `docs/diagramas/modelo_estrella.png`.

- **`dim_fecha`**: una fila por día calendario presente en los datos.
- **`dim_aeropuerto`**: una fila por código ICAO observado (como origen o destino), con posición aproximada estimada promediando las coordenadas de los puntos de despegue/aterrizaje de sus vuelos.
- **`fact_vuelo`**: una fila por vuelo, con claves foráneas a fecha y a los dos aeropuertos, y todas las métricas anteriores.
