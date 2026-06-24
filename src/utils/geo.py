"""Funciones geoespaciales usadas para derivar métricas de trayectoria."""
import numpy as np

RADIO_TIERRA_KM = 6371.0


def haversine_km(lat1, lon1, lat2, lon2):
    """Distancia ortodrómica entre dos puntos (arrays numpy o escalares), en km."""
    lat1, lon1, lat2, lon2 = map(np.radians, (lat1, lon1, lat2, lon2))
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = np.sin(dlat / 2.0) ** 2 + np.cos(lat1) * np.cos(lat2) * np.sin(dlon / 2.0) ** 2
    return 2 * RADIO_TIERRA_KM * np.arcsin(np.sqrt(a))


def metricas_track(track):
    """Calcula métricas agregadas de un track (lista de puntos {time, latitude,
    longitude, altitude, heading, onGround}) sin necesidad de persistirlo completo.
    """
    if track is None or len(track) == 0:
        return {
            "num_puntos_track": 0,
            "distancia_recorrida_km": None,
            "distancia_directa_km": None,
            "altitud_max_m": None,
            "altitud_promedio_m": None,
        }

    lats = np.array([p["latitude"] for p in track])
    lons = np.array([p["longitude"] for p in track])
    alts = np.array([p["altitude"] for p in track if p["altitude"] is not None])

    distancia_recorrida_km = None
    if len(lats) > 1:
        tramos = haversine_km(lats[:-1], lons[:-1], lats[1:], lons[1:])
        distancia_recorrida_km = float(np.nansum(tramos))

    distancia_directa_km = None
    if len(lats) > 1:
        distancia_directa_km = float(haversine_km(lats[0], lons[0], lats[-1], lons[-1]))

    return {
        "num_puntos_track": len(track),
        "distancia_recorrida_km": distancia_recorrida_km,
        "distancia_directa_km": distancia_directa_km,
        "altitud_max_m": float(np.nanmax(alts)) if len(alts) else None,
        "altitud_promedio_m": float(np.nanmean(alts)) if len(alts) else None,
    }


def punto_extremo(track, extremo="primero"):
    """Devuelve (lat, lon) del primer o último punto del track, o (None, None)."""
    if track is None or len(track) == 0:
        return None, None
    punto = track[0] if extremo == "primero" else track[-1]
    return punto["latitude"], punto["longitude"]
