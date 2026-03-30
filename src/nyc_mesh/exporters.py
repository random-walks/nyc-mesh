"""Exporters for browser-ready and analysis-ready outputs."""

from __future__ import annotations

import json
from typing import TYPE_CHECKING, Any

from ._not_implemented import planned_surface

if TYPE_CHECKING:
    from pathlib import Path

    from .models import BuildingFeature, ExportTarget


def export_geojson(data: tuple[BuildingFeature, ...], target: ExportTarget) -> Path:
    """Export WGS84 building features to a GeoJSON ``FeatureCollection``."""
    if target.format.lower() != "geojson":
        message = "export_geojson() requires ExportTarget.format to be 'geojson'."
        raise ValueError(message)

    output_path = target.output_path.expanduser()
    output_path.parent.mkdir(parents=True, exist_ok=True)

    features: list[dict[str, Any]] = []
    for feature in data:
        ring_coords = [
            [longitude, latitude] for longitude, latitude in feature.footprint_4326
        ]
        features.append(
            {
                "type": "Feature",
                "id": feature.building_id,
                "properties": {
                    "building_id": feature.building_id,
                    "height": feature.height,
                },
                "geometry": {
                    "type": "Polygon",
                    "coordinates": [ring_coords],
                },
            }
        )

    payload = {"type": "FeatureCollection", "features": features}
    output_path.write_text(f"{json.dumps(payload, indent=2)}\n", encoding="utf-8")
    return output_path.resolve()


def export_3d_tiles(_data: Any, _target: ExportTarget) -> Any:
    """Export a processed scene to Cesium-compatible 3D Tiles."""
    planned_surface("export_3d_tiles()")


def export_geoparquet(_data: Any, _target: ExportTarget) -> Any:
    """Export processed features to GeoParquet for analysis workflows."""
    planned_surface("export_geoparquet()")


def export_gltf(_data: Any, _target: ExportTarget) -> Any:
    """Export a lightweight glTF scene for generic 3D viewers."""
    planned_surface("export_gltf()")
