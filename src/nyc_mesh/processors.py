"""Processing steps for transforming raw NYC 3D inputs."""

from __future__ import annotations

from typing import Any

from pyproj import Transformer

from ._not_implemented import planned_surface
from .models import BoundingBox, BuildingFeature, CityGMLDataset, Coordinate2D

_TO_WGS84 = Transformer.from_crs("EPSG:2263", "EPSG:4326", always_xy=True)


def _normalise_ring(coords: tuple[Coordinate2D, ...]) -> tuple[Coordinate2D, ...]:
    if len(coords) < 3:
        return ()
    closed_ring = coords if coords[0] == coords[-1] else (*coords, coords[0])
    if len(set(closed_ring[:-1])) < 3:
        return ()
    return closed_ring


def _project_ring_to_wgs84(
    ring_2263: tuple[Coordinate2D, ...],
) -> tuple[Coordinate2D, ...]:
    projected: list[Coordinate2D] = []
    for x_coord, y_coord in ring_2263:
        lon, lat = _TO_WGS84.transform(x_coord, y_coord)
        projected.append((lon, lat))
    return _normalise_ring(tuple(projected))


def extract_buildings(citygml_data: CityGMLDataset) -> tuple[BuildingFeature, ...]:
    """Extract WGS84 footprints and measured heights from CityGML data."""
    extracted: list[BuildingFeature] = []
    for building in citygml_data.buildings:
        if building.measured_height is None:
            continue
        footprint_4326 = _project_ring_to_wgs84(building.footprint_2263)
        if not footprint_4326:
            continue
        extracted.append(
            BuildingFeature(
                building_id=building.building_id,
                footprint_4326=footprint_4326,
                height=building.measured_height,
            )
        )
    return tuple(extracted)


def clip_to_bbox(
    data: tuple[BuildingFeature, ...], bbox: BoundingBox
) -> tuple[BuildingFeature, ...]:
    """Clip height-aware building features to a WGS84 bounding box."""
    clipped: list[BuildingFeature] = []
    for feature in data:
        longitudes = tuple(coord[0] for coord in feature.footprint_4326)
        latitudes = tuple(coord[1] for coord in feature.footprint_4326)
        if not longitudes or not latitudes:
            continue
        ring_min_lon = min(longitudes)
        ring_max_lon = max(longitudes)
        ring_min_lat = min(latitudes)
        ring_max_lat = max(latitudes)

        disjoint = (
            ring_max_lon < bbox.min_lon
            or ring_min_lon > bbox.max_lon
            or ring_max_lat < bbox.min_lat
            or ring_min_lat > bbox.max_lat
        )
        if not disjoint:
            clipped.append(feature)
    return tuple(clipped)


def join_pluto(buildings: Any, pluto_data: Any) -> Any:
    """Join optional PLUTO tax lot attributes onto extracted buildings."""
    _ = buildings, pluto_data
    planned_surface("join_pluto()")


def generate_terrain_mesh(lidar_or_dem_data: Any) -> Any:
    """Generate a lightweight terrain mesh from elevation inputs."""
    _ = lidar_or_dem_data
    planned_surface("generate_terrain_mesh()")
