from __future__ import annotations

import json
from pathlib import Path

import pyarrow.parquet as pq

from nyc_mesh import analysis, export, pipeline
from nyc_mesh.io import load_dem
from nyc_mesh.models import ExportTarget
from tests.helpers import sample_citygml_path, write_dem_json


def test_export_geojson_geoparquet_gltf_and_3d_tiles(tmp_path: Path) -> None:
    features = pipeline.extract_citygml_buildings(sample_citygml_path())
    geojson_path = export.export_geojson(
        features,
        ExportTarget("geojson", tmp_path / "buildings.geojson"),
    )
    geoparquet_path = export.export_geoparquet(
        features,
        ExportTarget("geoparquet", tmp_path / "buildings.parquet"),
    )
    gltf_path = export.export_gltf(
        features,
        ExportTarget("gltf", tmp_path / "buildings.gltf"),
    )
    tileset_path = export.export_3d_tiles(
        features,
        ExportTarget("3dtiles", tmp_path / "tileset.json"),
    )

    geojson_payload = json.loads(geojson_path.read_text(encoding="utf-8"))
    assert geojson_payload["type"] == "FeatureCollection"
    assert len(geojson_payload["features"]) == 2

    parquet_table = pq.read_table(geoparquet_path)
    assert parquet_table.num_rows == 2
    assert b"geo" in (parquet_table.schema.metadata or {})

    gltf_payload = json.loads(gltf_path.read_text(encoding="utf-8"))
    assert gltf_payload["asset"]["version"] == "2.0"
    assert len(gltf_payload["meshes"]) == 1

    tileset_payload = json.loads(tileset_path.read_text(encoding="utf-8"))
    assert tileset_payload["root"]["content"]["uri"] == "content.gltf"
    assert (tmp_path / "content.gltf").exists()


def test_export_gltf_accepts_terrain_mesh(tmp_path: Path) -> None:
    dem_path = tmp_path / "sample-dem.json"
    write_dem_json(dem_path)
    mesh = analysis.generate_terrain_mesh(load_dem(dem_path))

    gltf_path = export.export_gltf(mesh, ExportTarget("gltf", tmp_path / "terrain.gltf"))
    gltf_payload = json.loads(gltf_path.read_text(encoding="utf-8"))

    assert gltf_payload["asset"]["generator"] == "nyc-mesh"
