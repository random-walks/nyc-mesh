"""Exporters for browser-ready and analysis-ready ``nyc-mesh`` outputs."""

from __future__ import annotations

import base64
import json
import math
import struct
from typing import TYPE_CHECKING

from ..io._geo import region_from_bounds
from ..models import (
    BoundingBox,
    ExportTarget,
    TerrainMeshDataset,
)

if TYPE_CHECKING:
    from pathlib import Path

    from ..models import BuildingFeature

try:  # pragma: no cover - exercised when dependency is installed
    import pyarrow as pa
    import pyarrow.parquet as pq
except ImportError:  # pragma: no cover - fallback for environments without pyarrow
    pa = None
    pq = None


def _validate_target_format(
    target: ExportTarget,
    *,
    expected_formats: tuple[str, ...],
) -> Path:
    output_format = target.format.lower()
    if output_format not in expected_formats:
        message = (
            f"Expected export target format in {expected_formats!r}, "
            f"got {target.format!r}."
        )
        raise ValueError(message)
    output_path = target.output_path.expanduser().resolve()
    output_path.parent.mkdir(parents=True, exist_ok=True)
    return output_path


def export_geojson(data: tuple[BuildingFeature, ...], target: ExportTarget) -> Path:
    """Export WGS84 building features to a GeoJSON ``FeatureCollection``."""

    output_path = _validate_target_format(target, expected_formats=("geojson",))
    payload = {
        "type": "FeatureCollection",
        "features": [
            {
                "type": "Feature",
                "id": feature.building_id,
                "properties": {
                    "building_id": feature.building_id,
                    "height": feature.height,
                    **feature.properties,
                },
                "geometry": {
                    "type": "Polygon",
                    "coordinates": [
                        [
                            [longitude, latitude]
                            for longitude, latitude in feature.footprint_4326
                        ]
                    ],
                },
            }
            for feature in data
        ],
    }
    output_path.write_text(f"{json.dumps(payload, indent=2)}\n", encoding="utf-8")
    return output_path


def _polygon_to_wkb(ring: tuple[tuple[float, float], ...]) -> bytes:
    """Encode a simple polygon ring as little-endian WKB."""

    ring_count = 1
    point_count = len(ring)
    header = struct.pack("<bI", 1, 3)
    body = struct.pack("<I", ring_count) + struct.pack("<I", point_count)
    points = b"".join(struct.pack("<dd", point[0], point[1]) for point in ring)
    return header + body + points


def export_geoparquet(data: tuple[BuildingFeature, ...], target: ExportTarget) -> Path:
    """Export building features to GeoParquet using a WKB geometry column."""

    if pa is None or pq is None:
        message = "GeoParquet export requires the optional `pyarrow` dependency."
        raise RuntimeError(message)

    output_path = _validate_target_format(
        target, expected_formats=("parquet", "geoparquet")
    )
    building_ids = [feature.building_id for feature in data]
    heights = [feature.height for feature in data]
    properties_json = [
        json.dumps(feature.properties, sort_keys=True) for feature in data
    ]
    geometries = [_polygon_to_wkb(feature.footprint_4326) for feature in data]
    table = pa.table(
        {
            "building_id": building_ids,
            "height": heights,
            "properties_json": properties_json,
            "geometry": geometries,
        }
    )
    geo_metadata = {
        "version": "1.1.0",
        "primary_column": "geometry",
        "columns": {
            "geometry": {
                "encoding": "WKB",
                "geometry_types": ["Polygon"],
                "crs": "OGC:CRS84",
            }
        },
    }
    table = table.replace_schema_metadata(
        {
            **(table.schema.metadata or {}),
            b"geo": json.dumps(geo_metadata).encode("utf-8"),
        }
    )
    pq.write_table(table, output_path)
    return output_path


def _local_xy(
    longitude: float,
    latitude: float,
    *,
    origin_lon: float,
    origin_lat: float,
) -> tuple[float, float]:
    mean_lat_radians = math.radians(origin_lat)
    x_coord = (longitude - origin_lon) * 111_320.0 * math.cos(mean_lat_radians)
    y_coord = (latitude - origin_lat) * 110_540.0
    return (x_coord, y_coord)


def _building_mesh(
    data: tuple[BuildingFeature, ...],
) -> tuple[list[tuple[float, float, float]], list[int]]:
    if not data:
        return ([], [])
    origin_lon, origin_lat = data[0].centroid
    vertices: list[tuple[float, float, float]] = []
    indices: list[int] = []

    for feature in data:
        ring = feature.footprint_4326[:-1]
        if len(ring) < 3:
            continue
        base_start = len(vertices)
        for longitude, latitude in ring:
            x_coord, y_coord = _local_xy(
                longitude,
                latitude,
                origin_lon=origin_lon,
                origin_lat=origin_lat,
            )
            vertices.append((x_coord, y_coord, 0.0))
        top_start = len(vertices)
        for longitude, latitude in ring:
            x_coord, y_coord = _local_xy(
                longitude,
                latitude,
                origin_lon=origin_lon,
                origin_lat=origin_lat,
            )
            vertices.append((x_coord, y_coord, feature.height))

        for index in range(1, len(ring) - 1):
            indices.extend((top_start, top_start + index, top_start + index + 1))

        for index in range(len(ring)):
            next_index = (index + 1) % len(ring)
            indices.extend(
                (
                    base_start + index,
                    base_start + next_index,
                    top_start + next_index,
                    base_start + index,
                    top_start + next_index,
                    top_start + index,
                )
            )
    return (vertices, indices)


def _terrain_mesh(
    data: TerrainMeshDataset,
) -> tuple[list[tuple[float, float, float]], list[int]]:
    vertices = list(data.vertices)
    indices = [index for triangle in data.triangles for index in triangle]
    return (vertices, indices)


def _build_gltf_json(
    vertices: list[tuple[float, float, float]],
    indices: list[int],
) -> dict[str, object]:
    if not vertices or not indices:
        message = "export_gltf() requires at least one mesh with vertices and indices."
        raise ValueError(message)

    position_blob = b"".join(struct.pack("<fff", *vertex) for vertex in vertices)
    index_blob = b"".join(struct.pack("<I", index) for index in indices)
    buffer_blob = position_blob + index_blob
    uri = "data:application/octet-stream;base64," + base64.b64encode(
        buffer_blob
    ).decode("ascii")
    mins = [min(vertex[axis] for vertex in vertices) for axis in range(3)]
    maxs = [max(vertex[axis] for vertex in vertices) for axis in range(3)]

    return {
        "asset": {"version": "2.0", "generator": "nyc-mesh"},
        "buffers": [{"byteLength": len(buffer_blob), "uri": uri}],
        "bufferViews": [
            {
                "buffer": 0,
                "byteOffset": 0,
                "byteLength": len(position_blob),
                "target": 34962,
            },
            {
                "buffer": 0,
                "byteOffset": len(position_blob),
                "byteLength": len(index_blob),
                "target": 34963,
            },
        ],
        "accessors": [
            {
                "bufferView": 0,
                "componentType": 5126,
                "count": len(vertices),
                "type": "VEC3",
                "min": mins,
                "max": maxs,
            },
            {
                "bufferView": 1,
                "componentType": 5125,
                "count": len(indices),
                "type": "SCALAR",
                "min": [min(indices)],
                "max": [max(indices)],
            },
        ],
        "meshes": [{"primitives": [{"attributes": {"POSITION": 0}, "indices": 1}]}],
        "nodes": [{"mesh": 0}],
        "scenes": [{"nodes": [0]}],
        "scene": 0,
    }


def export_gltf(
    data: tuple[BuildingFeature, ...] | TerrainMeshDataset,
    target: ExportTarget,
) -> Path:
    """Export a lightweight glTF scene for 3D viewers."""

    output_path = _validate_target_format(target, expected_formats=("gltf",))
    if isinstance(data, TerrainMeshDataset):
        vertices, indices = _terrain_mesh(data)
    else:
        vertices, indices = _building_mesh(data)
    gltf_payload = _build_gltf_json(vertices, indices)
    output_path.write_text(f"{json.dumps(gltf_payload, indent=2)}\n", encoding="utf-8")
    return output_path


def _feature_bounds(data: tuple[BuildingFeature, ...]) -> BoundingBox:
    min_lat = min(point[1] for feature in data for point in feature.footprint_4326)
    min_lon = min(point[0] for feature in data for point in feature.footprint_4326)
    max_lat = max(point[1] for feature in data for point in feature.footprint_4326)
    max_lon = max(point[0] for feature in data for point in feature.footprint_4326)
    return BoundingBox(
        min_lat=min_lat,
        min_lon=min_lon,
        max_lat=max_lat,
        max_lon=max_lon,
    )


def export_3d_tiles(data: tuple[BuildingFeature, ...], target: ExportTarget) -> Path:
    """Export a minimal Cesium 3D Tiles package backed by a glTF payload."""

    output_path = _validate_target_format(target, expected_formats=("3dtiles", "json"))
    if not data:
        message = "export_3d_tiles() requires at least one building feature."
        raise ValueError(message)

    gltf_path = output_path.parent / "content.gltf"
    export_gltf(data, ExportTarget(format="gltf", output_path=gltf_path))

    bounds = _feature_bounds(data)
    max_height = max(feature.height for feature in data)
    payload = {
        "asset": {"version": "1.1"},
        "extensionsUsed": ["3DTILES_content_gltf"],
        "extensionsRequired": ["3DTILES_content_gltf"],
        "geometricError": 0.0,
        "root": {
            "boundingVolume": {
                "region": region_from_bounds(
                    bounds,
                    min_height=0.0,
                    max_height=max_height,
                )
            },
            "geometricError": 0.0,
            "refine": "ADD",
            "content": {"uri": gltf_path.name},
        },
    }
    output_path.write_text(f"{json.dumps(payload, indent=2)}\n", encoding="utf-8")
    return output_path
