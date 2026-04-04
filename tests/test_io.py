from __future__ import annotations

from pathlib import Path

import pytest

from nyc_mesh.io import load_citygml, load_dem, load_footprints, load_lidar
from nyc_mesh.samples import load_sample_citygml
from tests.helpers import (
    sample_citygml_path,
    write_citygml_zip,
    write_dem_json,
    write_dem_tif,
    write_footprints_geojson,
    write_lidar_json,
)


def test_load_citygml_and_sample_loader() -> None:
    dataset = load_citygml(sample_citygml_path())
    sample_dataset = load_sample_citygml()

    assert len(dataset.buildings) == 3
    assert dataset.buildings[0].building_id == "building-inside"
    assert sample_dataset == dataset


def test_load_citygml_rejects_http_sources() -> None:
    with pytest.raises(ValueError, match="local file paths only"):
        load_citygml("https://example.com/buildings.gml")


def test_load_citygml_from_zip(tmp_path: Path) -> None:
    zip_path = tmp_path / "sample-citygml.zip"
    write_citygml_zip(zip_path)

    dataset = load_citygml(zip_path)

    assert len(dataset.buildings) == 3


def test_load_lidar_and_dem_from_json(tmp_path: Path) -> None:
    lidar_path = tmp_path / "sample-lidar.json"
    dem_path = tmp_path / "sample-dem.json"
    write_lidar_json(lidar_path)
    write_dem_json(dem_path)

    lidar = load_lidar(lidar_path)
    dem = load_dem(dem_path)

    assert len(lidar.points) == 4
    assert dem.rows == 3
    assert dem.cols == 3


def test_load_dem_from_geotiff(tmp_path: Path) -> None:
    dem_path = tmp_path / "sample-dem.tif"
    write_dem_tif(dem_path)

    dem = load_dem(dem_path)

    assert dem.rows == 3
    assert dem.cols == 3
    assert dem.crs == "EPSG:2263"


def test_load_footprints_from_geojson(tmp_path: Path) -> None:
    footprint_path = tmp_path / "footprints.geojson"
    write_footprints_geojson(footprint_path)

    footprints = load_footprints(footprint_path)

    assert len(footprints.features) == 2
    assert footprints.features[0].properties["land_use"] == "mixed"
