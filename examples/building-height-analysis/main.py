from __future__ import annotations

import json
from pathlib import Path

from nyc_mesh import analysis, export, io, models, pipeline, samples

ROOT = Path(__file__).resolve().parent
CACHE_DIR = ROOT / "cache"
ARTIFACTS_DIR = ROOT / "artifacts"
REPORTS_DIR = ROOT / "reports"


def cache_path(filename: str) -> Path:
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    return CACHE_DIR / filename


def artifact_path(filename: str) -> Path:
    ARTIFACTS_DIR.mkdir(parents=True, exist_ok=True)
    return ARTIFACTS_DIR / filename


def report_path(filename: str) -> Path:
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    return REPORTS_DIR / filename


def _write_dem(path: Path) -> None:
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


def _write_lidar(path: Path) -> None:
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


def main() -> None:
    features = pipeline.extract_citygml_buildings(samples.DEFAULT_SAMPLE_CITYGML)
    dem_path = cache_path("sample-dem.json")
    lidar_path = cache_path("sample-lidar.json")
    _write_dem(dem_path)
    _write_lidar(lidar_path)

    dem_mesh = analysis.generate_terrain_mesh(io.load_dem(dem_path))
    lidar_mesh = analysis.generate_terrain_mesh(io.load_lidar(lidar_path))

    parquet_path = pipeline.export_citygml_geoparquet(
        samples.DEFAULT_SAMPLE_CITYGML,
        artifact_path("buildings.parquet"),
    )
    terrain_gltf_path = export.export_gltf(
        dem_mesh,
        models.ExportTarget("gltf", artifact_path("terrain.gltf")),
    )
    tileset_path = export.export_3d_tiles(
        features,
        models.ExportTarget("3dtiles", artifact_path("tileset.json")),
    )

    heights = [feature.height for feature in features]
    report = f"""# Building Height Analysis Tearsheet

## Summary

- Buildings analysed: {len(features)}
- Minimum height: {min(heights):.1f}
- Maximum height: {max(heights):.1f}
- DEM mesh triangles: {len(dem_mesh.triangles)}
- LiDAR mesh triangles: {len(lidar_mesh.triangles)}

## Artifacts

- GeoParquet: `{parquet_path.name}`
- Terrain glTF: `{terrain_gltf_path.name}`
- Tileset: `{tileset_path.name}`
"""
    tearsheet_path = report_path("building-height-analysis-tearsheet.md")
    tearsheet_path.write_text(report, encoding="utf-8")

    print(f"Wrote {parquet_path}")
    print(f"Wrote {terrain_gltf_path}")
    print(f"Wrote {tileset_path}")
    print(f"Wrote {tearsheet_path}")


if __name__ == "__main__":
    main()
