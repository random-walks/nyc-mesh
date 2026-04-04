"""High-level pipeline helpers for ``nyc-mesh``."""

from __future__ import annotations

from pathlib import Path

from .analysis import clip_to_bbox, extract_buildings
from .export import export_geojson, export_geoparquet
from .io import load_citygml
from .models import BoundingBox, BuildingFeature, ExportTarget

__all__ = [
    "export_citygml_geojson",
    "export_citygml_geoparquet",
    "extract_citygml_buildings",
]


def extract_citygml_buildings(
    source: str | Path,
    *,
    bbox: BoundingBox | None = None,
) -> tuple[BuildingFeature, ...]:
    """Load local CityGML, extract buildings, and optionally clip the result."""

    dataset = load_citygml(source)
    buildings = extract_buildings(dataset)
    return clip_to_bbox(buildings, bbox) if bbox is not None else buildings


def export_citygml_geojson(
    source: str | Path,
    output_path: str | Path,
    *,
    bbox: BoundingBox | None = None,
) -> Path:
    """Run the CityGML happy path and write GeoJSON."""

    buildings = extract_citygml_buildings(source, bbox=bbox)
    target = ExportTarget(format="geojson", output_path=Path(output_path).expanduser())
    return export_geojson(buildings, target)


def export_citygml_geoparquet(
    source: str | Path,
    output_path: str | Path,
    *,
    bbox: BoundingBox | None = None,
) -> Path:
    """Run the CityGML happy path and write GeoParquet."""

    buildings = extract_citygml_buildings(source, bbox=bbox)
    target = ExportTarget(format="geoparquet", output_path=Path(output_path).expanduser())
    return export_geoparquet(buildings, target)
