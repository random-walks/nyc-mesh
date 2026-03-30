"""Planned exporters for browser-ready and analysis-ready outputs."""

from __future__ import annotations

from typing import Any

from ._not_implemented import planned_surface
from .models import ExportTarget


def export_geojson(data: Any, target: ExportTarget) -> Any:
    """Export height-aware building data to GeoJSON."""
    planned_surface("export_geojson()")


def export_3d_tiles(data: Any, target: ExportTarget) -> Any:
    """Export a processed scene to Cesium-compatible 3D Tiles."""
    planned_surface("export_3d_tiles()")


def export_geoparquet(data: Any, target: ExportTarget) -> Any:
    """Export processed features to GeoParquet for analysis workflows."""
    planned_surface("export_geoparquet()")


def export_gltf(data: Any, target: ExportTarget) -> Any:
    """Export a lightweight glTF scene for generic 3D viewers."""
    planned_surface("export_gltf()")
