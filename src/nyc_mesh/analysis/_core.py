"""Analysis helpers for ``nyc-mesh``."""

from __future__ import annotations

from math import atan2

from ..io._geo import (
    bbox_intersects,
    point_in_polygon,
    project_ring_to_wgs84,
    ring_bounds,
)
from ..models import (
    BoundingBox,
    BuildingFeature,
    CityGMLDataset,
    Coordinate3D,
    DEMDataset,
    FootprintDataset,
    LidarDataset,
    TerrainMeshDataset,
)


def extract_buildings(citygml_data: CityGMLDataset) -> tuple[BuildingFeature, ...]:
    """Extract height-aware WGS84 building footprints from loaded CityGML data."""

    extracted: list[BuildingFeature] = []
    for building in citygml_data.buildings:
        if building.measured_height is None:
            continue
        footprint_4326 = project_ring_to_wgs84(building.footprint_2263)
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
    data: tuple[BuildingFeature, ...],
    bbox: BoundingBox,
) -> tuple[BuildingFeature, ...]:
    """Clip building features to a WGS84 bounding box."""

    return tuple(
        feature
        for feature in data
        if bbox_intersects(ring_bounds(feature.footprint_4326), bbox)
    )


def join_pluto(
    buildings: tuple[BuildingFeature, ...],
    pluto_data: FootprintDataset,
) -> tuple[BuildingFeature, ...]:
    """Join footprint properties onto buildings by id or centroid overlap."""

    features_by_id = {feature.feature_id: feature for feature in pluto_data.features}
    joined = []
    for building in buildings:
        match = features_by_id.get(building.building_id)
        if match is None:
            centroid = building.centroid
            for feature in pluto_data.features:
                bounds = ring_bounds(feature.footprint_4326)
                if bounds.contains(*centroid) and point_in_polygon(
                    centroid,
                    feature.footprint_4326,
                ):
                    match = feature
                    break
        if match is None:
            joined.append(building)
            continue
        joined.append(building.with_properties(match.properties))
    return tuple(joined)


def _terrain_mesh_from_dem(data: DEMDataset) -> TerrainMeshDataset:
    vertices: list[Coordinate3D] = []
    index_by_cell: dict[tuple[int, int], int] = {}
    rows = data.rows

    for row_index, row in enumerate(data.values):
        for col_index, value in enumerate(row):
            if value is None:
                continue
            x_coord = data.origin_x + (col_index * data.cell_size)
            y_coord = data.origin_y + ((rows - row_index - 1) * data.cell_size)
            index_by_cell[(row_index, col_index)] = len(vertices)
            vertices.append((x_coord, y_coord, value))

    triangles: list[tuple[int, int, int]] = []
    for row_index in range(rows - 1):
        for col_index in range(data.cols - 1):
            indices = (
                index_by_cell.get((row_index, col_index)),
                index_by_cell.get((row_index, col_index + 1)),
                index_by_cell.get((row_index + 1, col_index)),
                index_by_cell.get((row_index + 1, col_index + 1)),
            )
            if any(index is None for index in indices):
                continue
            top_left, top_right, bottom_left, bottom_right = indices
            assert top_left is not None
            assert top_right is not None
            assert bottom_left is not None
            assert bottom_right is not None
            triangles.append((top_left, bottom_left, top_right))
            triangles.append((top_right, bottom_left, bottom_right))

    return TerrainMeshDataset(
        source=str(data.source),
        vertices=tuple(vertices),
        triangles=tuple(triangles),
    )


def _terrain_mesh_from_lidar(data: LidarDataset) -> TerrainMeshDataset:
    if len(data.points) < 3:
        message = "At least three LiDAR points are required to build a terrain mesh."
        raise ValueError(message)

    centroid = (
        sum(point.x for point in data.points) / len(data.points),
        sum(point.y for point in data.points) / len(data.points),
        sum(point.z for point in data.points) / len(data.points),
    )
    ordered = sorted(
        data.points,
        key=lambda point: atan2(point.y - centroid[1], point.x - centroid[0]),
    )
    vertices: list[Coordinate3D] = [(point.x, point.y, point.z) for point in ordered]
    centroid_index = len(vertices)
    vertices.append(centroid)

    triangles = []
    for index in range(len(ordered)):
        next_index = (index + 1) % len(ordered)
        triangles.append((centroid_index, index, next_index))

    return TerrainMeshDataset(
        source=str(data.source),
        vertices=tuple(vertices),
        triangles=tuple(triangles),
    )


def generate_terrain_mesh(
    lidar_or_dem_data: LidarDataset | DEMDataset,
) -> TerrainMeshDataset:
    """Generate a lightweight terrain mesh from DEM or LiDAR inputs."""

    if isinstance(lidar_or_dem_data, DEMDataset):
        return _terrain_mesh_from_dem(lidar_or_dem_data)
    return _terrain_mesh_from_lidar(lidar_or_dem_data)
