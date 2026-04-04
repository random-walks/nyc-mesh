"""Shared geometry helpers for ``nyc-mesh``."""

from __future__ import annotations

from math import radians

from pyproj import Transformer

from ..models import BoundingBox, Coordinate2D

_TO_WGS84 = Transformer.from_crs("EPSG:2263", "EPSG:4326", always_xy=True)


def normalise_ring(coords: tuple[Coordinate2D, ...]) -> tuple[Coordinate2D, ...]:
    """Return a closed ring with at least three distinct points."""

    if len(coords) < 3:
        return ()
    closed_ring = coords if coords[0] == coords[-1] else (*coords, coords[0])
    if len(set(closed_ring[:-1])) < 3:
        return ()
    return closed_ring


def project_ring_to_wgs84(
    ring_2263: tuple[Coordinate2D, ...],
) -> tuple[Coordinate2D, ...]:
    """Project an EPSG:2263 ring to WGS84 coordinates."""

    projected = []
    for x_coord, y_coord in ring_2263:
        lon, lat = _TO_WGS84.transform(x_coord, y_coord)
        projected.append((lon, lat))
    return normalise_ring(tuple(projected))


def ring_bounds(ring: tuple[Coordinate2D, ...]) -> BoundingBox:
    """Return the WGS84 bounds of a ring."""

    longitudes = [coord[0] for coord in ring]
    latitudes = [coord[1] for coord in ring]
    return BoundingBox(
        min_lat=min(latitudes),
        min_lon=min(longitudes),
        max_lat=max(latitudes),
        max_lon=max(longitudes),
    )


def ring_centroid(ring: tuple[Coordinate2D, ...]) -> Coordinate2D:
    """Return the simple centroid average of a ring."""

    open_ring = ring[:-1] if ring else ()
    if not open_ring:
        return (0.0, 0.0)
    return (
        sum(point[0] for point in open_ring) / len(open_ring),
        sum(point[1] for point in open_ring) / len(open_ring),
    )


def bbox_intersects(a: BoundingBox, b: BoundingBox) -> bool:
    """Return whether two WGS84 bounding boxes intersect."""

    return not (
        a.max_lon < b.min_lon
        or a.min_lon > b.max_lon
        or a.max_lat < b.min_lat
        or a.min_lat > b.max_lat
    )


def point_in_polygon(point: Coordinate2D, ring: tuple[Coordinate2D, ...]) -> bool:
    """Return whether a WGS84 point lies inside a simple polygon ring."""

    if len(ring) < 4:
        return False

    inside = False
    x_coord, y_coord = point
    previous = ring[-1]
    for current in ring:
        x1, y1 = previous
        x2, y2 = current
        if ((y1 > y_coord) != (y2 > y_coord)) and (
            x_coord < (x2 - x1) * (y_coord - y1) / (y2 - y1 + 1e-12) + x1
        ):
            inside = not inside
        previous = current
    return inside


def region_from_bounds(bounds: BoundingBox, *, min_height: float, max_height: float) -> list[float]:
    """Return a Cesium region array for a WGS84 bounding box."""

    return [
        radians(bounds.min_lon),
        radians(bounds.min_lat),
        radians(bounds.max_lon),
        radians(bounds.max_lat),
        min_height,
        max_height,
    ]
