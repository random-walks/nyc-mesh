from __future__ import annotations

import json
from pathlib import Path

import pyarrow.parquet as pq

from nyc_mesh import pipeline
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
    assert [feature["id"] for feature in geojson_payload["features"]] == ["building-inside"]

    parquet_table = pq.read_table(geoparquet_path)
    assert parquet_table.num_rows == 2
