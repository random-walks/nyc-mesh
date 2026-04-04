from __future__ import annotations

import argparse
from pathlib import Path

from nyc_mesh import analysis, export, io, models, pipeline

ROOT = Path(__file__).resolve().parent
CACHE_DIR = ROOT / "cache"
ARTIFACTS_DIR = ROOT / "artifacts"
REPORTS_DIR = ROOT / "reports"


def cache_path(name: str) -> Path:
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    return CACHE_DIR / name


def artifact_path(name: str) -> Path:
    ARTIFACTS_DIR.mkdir(parents=True, exist_ok=True)
    return ARTIFACTS_DIR / name


def report_path(name: str) -> Path:
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    return REPORTS_DIR / name


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Build a real landmark-scale 3D stack from official NYC data.",
    )
    parser.add_argument(
        "--study-area",
        default="empire-state-building",
        choices=tuple(pipeline.DEFAULT_STUDY_AREAS),
    )
    parser.add_argument(
        "--cache-dir",
        type=Path,
        default=cache_path("empire-state-building"),
    )
    parser.add_argument("--citygml-path", type=Path)
    parser.add_argument("--allow-citygml-download", action="store_true")
    parser.add_argument("--dem-path", type=Path)
    parser.add_argument("--lidar-path", type=Path)
    parser.add_argument("--publish-report", action="store_true")
    return parser


def write_report(
    study_area: str,
    geojson_path: Path,
    geoparquet_path: Path,
    gltf_path: Path,
    tileset_path: Path,
    building_count: int,
    terrain_source: str | None,
) -> Path:
    report = f"""# Landmark 3D Stack Tearsheet

## Summary

- Study area: `{study_area}`
- Height-aware buildings exported: {building_count}
- Terrain source: `{terrain_source or 'none supplied'}`

## Artifacts

- GeoJSON: `{geojson_path.name}`
- GeoParquet: `{geoparquet_path.name}`
- glTF: `{gltf_path.name}`
- 3D Tiles: `{tileset_path.name}`
"""
    output_path = report_path("landmark-3d-stack-tearsheet.md")
    output_path.write_text(report, encoding="utf-8")
    return output_path


def main() -> None:
    args = build_parser().parse_args()
    bbox = pipeline.DEFAULT_STUDY_AREAS[args.study_area]
    manifest = pipeline.build_study_area_manifest(
        study_area_name=args.study_area,
        bbox=bbox,
        cache_dir=args.cache_dir,
        citygml_path=args.citygml_path,
        allow_citygml_download=args.allow_citygml_download,
        dem_path=args.dem_path,
        lidar_path=args.lidar_path,
    )
    buildings = pipeline.extract_manifest_buildings(manifest)
    geojson_path = export.export_geojson(
        buildings,
        models.ExportTarget("geojson", artifact_path("landmark-buildings.geojson")),
    )
    geoparquet_path = export.export_geoparquet(
        buildings,
        models.ExportTarget("geoparquet", artifact_path("landmark-buildings.parquet")),
    )
    gltf_path = export.export_gltf(
        buildings,
        models.ExportTarget("gltf", artifact_path("landmark-buildings.gltf")),
    )
    tileset_path = export.export_3d_tiles(
        buildings,
        models.ExportTarget("3dtiles", artifact_path("tileset.json")),
    )

    terrain_source_label: str | None = None
    if manifest.dem_source is not None:
        terrain_mesh = analysis.generate_terrain_mesh(io.load_dem(manifest.dem_source))
        export.export_gltf(
            terrain_mesh,
            models.ExportTarget("gltf", artifact_path("terrain.gltf")),
        )
        terrain_source_label = manifest.dem_source.name
    elif manifest.lidar_source is not None:
        terrain_mesh = analysis.generate_terrain_mesh(io.load_lidar(manifest.lidar_source))
        export.export_gltf(
            terrain_mesh,
            models.ExportTarget("gltf", artifact_path("terrain.gltf")),
        )
        terrain_source_label = manifest.lidar_source.name

    report_file: Path | None = None
    if args.publish_report:
        report_file = write_report(
            args.study_area,
            geojson_path,
            geoparquet_path,
            gltf_path,
            tileset_path,
            len(buildings),
            terrain_source_label,
        )

    print("Landmark 3D Stack")
    print("-----------------")
    print(f"Study area: {args.study_area}")
    print(f"CityGML source: {manifest.citygml_source}")
    print(f"Wrote {geojson_path}")
    print(f"Wrote {geoparquet_path}")
    print(f"Wrote {gltf_path}")
    print(f"Wrote {tileset_path}")
    if report_file is None:
        print("Skipped tracked report generation. Re-run with --publish-report to update reports/.")
    else:
        print(f"Wrote tracked report: {report_file}")


if __name__ == "__main__":
    main()
