from __future__ import annotations

import importlib.metadata
from pathlib import Path

import nyc_mesh as m
from nyc_mesh.models import BoundingBox, ExportTarget, NeighborhoodRequest


def test_version() -> None:
    assert importlib.metadata.version("nyc_mesh") == m.__version__


def test_planned_surface_is_importable() -> None:
    bbox = BoundingBox(min_lat=40.7, min_lon=-74.01, max_lat=40.72, max_lon=-73.99)
    request = NeighborhoodRequest(name="dumbo", bbox=bbox)
    target = ExportTarget(format="geojson", output_path=Path("dummy.geojson"))

    assert request.name == "dumbo"
    assert target.format == "geojson"
    assert callable(m.load_citygml)
    assert callable(m.extract_buildings)
    assert callable(m.export_geojson)
