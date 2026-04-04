from __future__ import annotations

from pathlib import Path

from nyc_mesh import pipeline, samples

ROOT = Path(__file__).resolve().parent
ARTIFACTS_DIR = ROOT / "artifacts"
REPORTS_DIR = ROOT / "reports"


def artifact_path(filename: str) -> Path:
    ARTIFACTS_DIR.mkdir(parents=True, exist_ok=True)
    return ARTIFACTS_DIR / filename


def report_path(filename: str) -> Path:
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    return REPORTS_DIR / filename


def main() -> None:
    source_path = samples.DEFAULT_SAMPLE_CITYGML
    features = pipeline.extract_citygml_buildings(source_path)
    geojson_path = pipeline.export_citygml_geojson(
        source_path,
        artifact_path("buildings.geojson"),
    )
    parquet_path = pipeline.export_citygml_geoparquet(
        source_path,
        artifact_path("buildings.parquet"),
    )

    max_height = max(feature.height for feature in features)
    report = f"""# Quickstart CityGML Tearsheet

## Summary

- Source file: `{source_path.name}`
- Height-aware buildings: {len(features)}
- Maximum measured height: {max_height:.1f}

## Artifacts

- GeoJSON: `{geojson_path.name}`
- GeoParquet: `{parquet_path.name}`
"""
    tearsheet_path = report_path("quickstart-citygml-tearsheet.md")
    tearsheet_path.write_text(report, encoding="utf-8")

    print(f"Wrote {geojson_path}")
    print(f"Wrote {parquet_path}")
    print(f"Wrote {tearsheet_path}")


if __name__ == "__main__":
    main()
