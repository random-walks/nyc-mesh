from __future__ import annotations

import json
from pathlib import Path

import pyarrow.parquet as pq
import pytest

from nyc_mesh import pipeline
from nyc_mesh.io import load_footprints
from nyc_mesh.models import BoundingBox
from tests.helpers import sample_citygml_path


def test_pipeline_helpers_export_geojson_and_geoparquet(tmp_path: Path) -> None:
    geojson_path = pipeline.export_citygml_geojson(
        sample_citygml_path(),
        tmp_path / "buildings.geojson",
        bbox=BoundingBox(
            min_lat=40.687,
            min_lon=-74.03,
            max_lat=40.705,
            max_lon=-74.0,
        ),
    )
    geoparquet_path = pipeline.export_citygml_geoparquet(
        sample_citygml_path(),
        tmp_path / "buildings.parquet",
    )

    geojson_payload = json.loads(geojson_path.read_text(encoding="utf-8"))
    assert [feature["id"] for feature in geojson_payload["features"]] == [
        "building-inside"
    ]

    parquet_table = pq.read_table(geoparquet_path)
    assert parquet_table.num_rows == 2


def test_build_study_area_manifest_writes_official_context_files(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    building = pipeline.extract_citygml_buildings(sample_citygml_path())[0]

    monkeypatch.setattr(
        pipeline,
        "fetch_pluto_records_for_bbox",
        lambda _bbox: [
            {"bbl": "1000000001.00000000", "address": "1 TEST PLAZA", "borough": "MN"}
        ],
    )
    monkeypatch.setattr(
        pipeline,
        "fetch_building_footprints_for_bbls",
        lambda _bbls: [
            {
                "the_geom": {
                    "type": "Polygon",
                    "coordinates": [
                        [[lon, lat] for lon, lat in building.footprint_4326]
                    ],
                },
                "bin": "1000001",
                "base_bbl": "1000000001",
                "mappluto_bbl": "1000000001",
                "height_roof": building.height,
                "ground_elevation": "0",
                "construction_year": "2000",
            }
        ],
    )

    manifest = pipeline.build_study_area_manifest(
        study_area_name="test-area",
        bbox=BoundingBox(
            min_lat=40.687,
            min_lon=-74.03,
            max_lat=40.705,
            max_lon=-74.0,
        ),
        cache_dir=tmp_path,
        citygml_path=sample_citygml_path(),
    )

    assert manifest.citygml_source == sample_citygml_path().resolve()
    assert manifest.footprints_source is not None
    assert manifest.footprints_source.exists()
    assert manifest.pluto_source is not None
    assert manifest.pluto_source.exists()
    assert (tmp_path / "asset-manifest.json").exists()
    assert len(load_footprints(manifest.footprints_source).features) == 1
