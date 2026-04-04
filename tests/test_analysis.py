from __future__ import annotations

from pathlib import Path

from nyc_mesh import analysis, pipeline
from nyc_mesh.io import load_dem, load_footprints, load_lidar
from nyc_mesh.models import BoundingBox
from tests.helpers import (
    sample_citygml_path,
    write_dem_json,
    write_footprints_geojson,
    write_lidar_json,
)


def test_extract_buildings_and_clip_to_bbox() -> None:
    features = pipeline.extract_citygml_buildings(sample_citygml_path())

    clipped = analysis.clip_to_bbox(
        features,
        BoundingBox(
            min_lat=40.687,
            min_lon=-74.03,
            max_lat=40.705,
            max_lon=-74.0,
        ),
    )

    assert {feature.building_id for feature in features} == {
        "building-inside",
        "building-outside",
    }
    assert [feature.building_id for feature in clipped] == ["building-inside"]


def test_join_pluto_merges_properties(tmp_path: Path) -> None:
    footprint_path = tmp_path / "footprints.geojson"
    write_footprints_geojson(footprint_path)
    features = pipeline.extract_citygml_buildings(sample_citygml_path())
    joined = analysis.join_pluto(features, load_footprints(footprint_path))

    assert joined[0].properties["bbl"] == "0000000001"
    assert joined[1].properties["land_use"] == "commercial"


def test_generate_terrain_mesh_from_dem_and_lidar(tmp_path: Path) -> None:
    dem_path = tmp_path / "sample-dem.json"
    lidar_path = tmp_path / "sample-lidar.json"
    write_dem_json(dem_path)
    write_lidar_json(lidar_path)

    dem_mesh = analysis.generate_terrain_mesh(load_dem(dem_path))
    lidar_mesh = analysis.generate_terrain_mesh(load_lidar(lidar_path))

    assert len(dem_mesh.vertices) == 9
    assert len(dem_mesh.triangles) == 8
    assert len(lidar_mesh.vertices) == 5
    assert len(lidar_mesh.triangles) == 4
