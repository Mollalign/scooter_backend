"""Geo helpers — coordinate conversions and PostGIS ewkt wrappers."""

from math import asin, cos, radians, sin, sqrt

EARTH_RADIUS_M = 6_371_000.0


def haversine_m(lat1: float, lng1: float, lat2: float, lng2: float) -> float:
    """Great-circle distance between two points, metres."""
    lat1r, lat2r = radians(lat1), radians(lat2)
    dlat = lat2r - lat1r
    dlng = radians(lng2 - lng1)
    a = sin(dlat / 2) ** 2 + cos(lat1r) * cos(lat2r) * sin(dlng / 2) ** 2
    return 2 * EARTH_RADIUS_M * asin(sqrt(a))


def wkt_point(lat: float, lng: float) -> str:
    """PostGIS POINT ewkt string (SRID 4326)."""
    return f"SRID=4326;POINT({lng} {lat})"


def point_to_lat_lng(point) -> tuple[float, float] | None:
    """Extract (lat, lng) from a GeoAlchemy2 POINT, or None."""
    if point is None:
        return None
    try:
        from geoalchemy2.shape import to_shape

        shape = to_shape(point)
        return shape.y, shape.x
    except Exception:   # noqa: BLE001
        return None
