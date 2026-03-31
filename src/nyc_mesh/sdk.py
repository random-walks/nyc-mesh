"""High-level SDK helpers for the implemented v0.1 CityGML workflow."""

from __future__ import annotations

from pathlib import Path

from .exporters import export_geojson
from .loaders import load_citygml
from .models import BoundingBox, BuildingFeature, ExportTarget
from .processors import clip_to_bbox, extract_buildings


def extract_citygml_buildings(
    source: str | Path, *, bbox: BoundingBox | None = None
) -> tuple[BuildingFeature, ...]:
    """Load local CityGML, extract height-aware buildings, and optionally clip.

    This convenience helper keeps the current narrow v0.1 assumptions intact:

    - only local CityGML files are supported
    - only buildings with ``bldg:measuredHeight`` are retained
    - source coordinates are treated as ``EPSG:2263`` before reprojection to
      ``EPSG:4326``
    - clipping, when requested, uses a WGS84 bounding box
    """
    dataset = load_citygml(source)
    buildings = extract_buildings(dataset)
    return clip_to_bbox(buildings, bbox) if bbox is not None else buildings


def export_citygml_geojson(
    source: str | Path,
    output_path: str | Path,
    *,
    bbox: BoundingBox | None = None,
) -> Path:
    """Run the implemented CityGML happy path and write GeoJSON."""
    target = ExportTarget(format="geojson", output_path=Path(output_path).expanduser())
    buildings = extract_citygml_buildings(source, bbox=bbox)
    return export_geojson(buildings, target)
