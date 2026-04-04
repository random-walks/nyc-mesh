from __future__ import annotations

import argparse
from pathlib import Path

import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d.art3d import Poly3DCollection

from nyc_mesh import export, models, pipeline

ROOT = Path(__file__).resolve().parent
CACHE_DIR = ROOT / "cache"
ARTIFACTS_DIR = ROOT / "artifacts"
REPORTS_DIR = ROOT / "reports"
FIGURES_DIR = REPORTS_DIR / "figures"


def cache_path(name: str) -> Path:
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    return CACHE_DIR / name


def artifact_path(name: str) -> Path:
    ARTIFACTS_DIR.mkdir(parents=True, exist_ok=True)
    return ARTIFACTS_DIR / name


def report_path(name: str) -> Path:
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    return REPORTS_DIR / name


def figure_path(name: str) -> Path:
    FIGURES_DIR.mkdir(parents=True, exist_ok=True)
    return FIGURES_DIR / name


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Plot a real building-height study from official NYC 3D data.",
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
    parser.add_argument("--citygml-path", type=Path, required=True)
    parser.add_argument("--publish-report", action="store_true")
    return parser


def _building_faces(feature: models.BuildingFeature) -> list[list[tuple[float, float, float]]]:
    ring = feature.footprint_4326[:-1]
    if len(ring) < 3:
        return []
    min_lon = min(point[0] for point in ring)
    min_lat = min(point[1] for point in ring)
    faces = []
    roof = []
    base = []
    for lon, lat in ring:
        x_coord = (lon - min_lon) * 111_320
        y_coord = (lat - min_lat) * 110_540
        base.append((x_coord, y_coord, 0.0))
        roof.append((x_coord, y_coord, feature.height))
    faces.append(roof)
    for index in range(len(ring)):
        next_index = (index + 1) % len(ring)
        faces.append(
            [
                base[index],
                base[next_index],
                roof[next_index],
                roof[index],
            ]
        )
    return faces


def write_report(study_area: str, heights: list[float], geoparquet_path: Path) -> Path:
    report = f"""# Building Height Analysis Tearsheet

## Summary

- Study area: `{study_area}`
- Buildings analysed: {len(heights)}
- Minimum height: {min(heights):.1f}
- Maximum height: {max(heights):.1f}
- Median-like middle value: {sorted(heights)[len(heights) // 2]:.1f}

## Artifacts

- GeoParquet: `{geoparquet_path.name}`

## Figures

- `./figures/view-southwest.png`
- `./figures/view-east.png`
- `./figures/view-topdown.png`
"""
    output_path = report_path("building-height-analysis-tearsheet.md")
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
    )
    buildings = pipeline.extract_manifest_buildings(manifest)
    geoparquet_path = export.export_geoparquet(
        buildings,
        models.ExportTarget("geoparquet", artifact_path("building-heights.parquet")),
    )

    for azimuth, elevation, filename in (
        (220, 24, "view-southwest.png"),
        (95, 18, "view-east.png"),
        (0, 90, "view-topdown.png"),
    ):
        figure = plt.figure(figsize=(8, 8))
        axes = figure.add_subplot(111, projection="3d")
        for feature in buildings:
            faces = _building_faces(feature)
            if not faces:
                continue
            collection = Poly3DCollection(
                faces,
                alpha=0.4,
                linewidths=0.4,
                edgecolors="#222222",
            )
            collection.set_facecolor("#4f83cc")
            axes.add_collection3d(collection)
        axes.view_init(elev=elevation, azim=azimuth)
        axes.set_title(f"{args.study_area} building heights")
        axes.set_xlabel("Local X")
        axes.set_ylabel("Local Y")
        axes.set_zlabel("Height")
        figure.savefig(figure_path(filename), dpi=180, bbox_inches="tight")
        plt.close(figure)

    report_file: Path | None = None
    if args.publish_report:
        report_file = write_report(
            args.study_area,
            [feature.height for feature in buildings],
            geoparquet_path,
        )

    print("Building Height Analysis")
    print("------------------------")
    print(f"Study area: {args.study_area}")
    print(f"CityGML source: {manifest.citygml_source}")
    print(f"Wrote {geoparquet_path}")
    if report_file is None:
        print("Skipped tracked report generation. Re-run with --publish-report to update reports/.")
    else:
        print(f"Wrote tracked report: {report_file}")


if __name__ == "__main__":
    main()
