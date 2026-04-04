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


def _write_pluto_stub(path: Path, features: tuple[models.BuildingFeature, ...]) -> None:
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
                        [[longitude, latitude] for longitude, latitude in feature.footprint_4326]
                    ],
                },
            }
            for index, feature in enumerate(features)
        ],
    }
    path.write_text(json.dumps(payload), encoding="utf-8")


def main() -> None:
    bbox = models.BoundingBox(
        min_lat=40.687,
        min_lon=-74.03,
        max_lat=40.705,
        max_lon=-74.0,
    )
    clipped = pipeline.extract_citygml_buildings(samples.DEFAULT_SAMPLE_CITYGML, bbox=bbox)
    pluto_path = cache_path("pluto-footprints.geojson")
    _write_pluto_stub(pluto_path, clipped)
    joined = analysis.join_pluto(clipped, io.load_footprints(pluto_path))
    output_path = export.export_geojson(
        joined,
        models.ExportTarget("geojson", artifact_path("neighborhood-buildings.geojson")),
    )

    report = f"""# Neighborhood Clip Tearsheet

## Summary

- Buildings in clip: {len(clipped)}
- Joined buildings: {len(joined)}
- Example BBL: {joined[0].properties.get("bbl")}

## Artifact

- GeoJSON: `{output_path.name}`
"""
    tearsheet_path = report_path("neighborhood-clip-tearsheet.md")
    tearsheet_path.write_text(report, encoding="utf-8")

    print(f"Wrote {pluto_path}")
    print(f"Wrote {output_path}")
    print(f"Wrote {tearsheet_path}")


if __name__ == "__main__":
    main()
