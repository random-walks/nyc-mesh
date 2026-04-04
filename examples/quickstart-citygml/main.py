from __future__ import annotations

import argparse
from pathlib import Path

from nyc_mesh import pipeline

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
        description="Build a real CityGML cache manifest and export quickstart outputs.",
    )
    parser.add_argument(
        "--study-area",
        default="lower-manhattan-skyline",
        choices=tuple(pipeline.DEFAULT_STUDY_AREAS),
    )
    parser.add_argument(
        "--cache-dir",
        type=Path,
        default=cache_path("lower-manhattan-skyline"),
    )
    parser.add_argument("--citygml-path", type=Path)
    parser.add_argument("--allow-citygml-download", action="store_true")
    parser.add_argument("--publish-report", action="store_true")
    return parser


def write_report(
    study_area: str,
    geojson_path: Path,
    geoparquet_path: Path,
    building_count: int,
) -> Path:
    report = f"""# Quickstart CityGML Tearsheet

## Summary

- Study area: `{study_area}`
- Height-aware buildings exported: {building_count}

## Artifacts

- GeoJSON: `{geojson_path.name}`
- GeoParquet: `{geoparquet_path.name}`
"""
    output_path = report_path("quickstart-citygml-tearsheet.md")
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
    )
    buildings = pipeline.extract_manifest_buildings(manifest)
    geojson_path = pipeline.export_citygml_geojson(
        manifest.citygml_source,
        artifact_path("buildings.geojson"),
        bbox=bbox,
    )
    geoparquet_path = pipeline.export_citygml_geoparquet(
        manifest.citygml_source,
        artifact_path("buildings.parquet"),
        bbox=bbox,
    )

    report_file: Path | None = None
    if args.publish_report:
        report_file = write_report(
            args.study_area,
            geojson_path,
            geoparquet_path,
            len(buildings),
        )

    print("Quickstart CityGML")
    print("------------------")
    print(f"Study area: {args.study_area}")
    print(f"CityGML source: {manifest.citygml_source}")
    print(f"Wrote {geojson_path}")
    print(f"Wrote {geoparquet_path}")
    if report_file is None:
        print(
            "Skipped tracked report generation. Re-run with --publish-report to update reports/."
        )
    else:
        print(f"Wrote tracked report: {report_file}")


if __name__ == "__main__":
    main()
