from __future__ import annotations

import json
import zipfile
from pathlib import Path

import numpy as np
import rasterio
from rasterio.transform import from_origin

from nyc_mesh import pipeline, samples


def sample_citygml_path() -> Path:
    return samples.DEFAULT_SAMPLE_CITYGML


def write_footprints_geojson(path: Path) -> None:
    features = pipeline.extract_citygml_buildings(sample_citygml_path())
    payload = {
        "type": "FeatureCollection",
        "features": [
            {
                "type": "Feature",
                "id": feature.building_id,
                "properties": {
                    "building_id": feature.building_id,
                    "bbl": f"{index + 1:010d}",
                    "land_use": "mixed" if index == 0 else "commercial",
                },
                "geometry": {
                    "type": "Polygon",
                    "coordinates": [
                        [
                            [longitude, latitude]
                            for longitude, latitude in feature.footprint_4326
                        ]
                    ],
                },
            }
            for index, feature in enumerate(features)
        ],
    }
    path.write_text(json.dumps(payload), encoding="utf-8")


def write_dem_json(path: Path) -> None:
    path.write_text(
        json.dumps(
            {
                "origin_x": 981000,
                "origin_y": 190000,
                "cell_size": 50,
                "nodata": None,
                "crs": "EPSG:2263",
                "values": [
                    [8.0, 9.0, 10.0],
                    [7.5, 8.5, 9.5],
                    [7.0, 8.0, 9.0],
                ],
            }
        ),
        encoding="utf-8",
    )


def write_lidar_json(path: Path) -> None:
    path.write_text(
        json.dumps(
            {
                "points": [
                    {"x": 981000, "y": 190000, "z": 8.0},
                    {"x": 981050, "y": 190000, "z": 8.5},
                    {"x": 981050, "y": 190050, "z": 9.0},
                    {"x": 981000, "y": 190050, "z": 8.4},
                ]
            }
        ),
        encoding="utf-8",
    )


def write_citygml_zip(path: Path) -> None:
    with zipfile.ZipFile(path, "w") as archive:
        archive.write(sample_citygml_path(), arcname="sample.gml")


def write_dem_tif(path: Path) -> None:
    data = np.array(
        [
            [8.0, 9.0, 10.0],
            [7.5, 8.5, 9.5],
            [7.0, 8.0, 9.0],
        ],
        dtype="float32",
    )
    with rasterio.open(
        path,
        "w",
        driver="GTiff",
        height=data.shape[0],
        width=data.shape[1],
        count=1,
        dtype=data.dtype,
        crs="EPSG:2263",
        transform=from_origin(981000, 190150, 50, 50),
        nodata=-9999,
    ) as dataset:
        dataset.write(data, 1)
