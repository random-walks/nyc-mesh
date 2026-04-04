"""High-level pipeline helpers for ``nyc-mesh``."""

from __future__ import annotations

import json
from pathlib import Path

from .analysis import clip_to_bbox, extract_buildings, join_pluto
from .export import export_geojson, export_geoparquet
from .io import (
    NYC_BUILDING_FOOTPRINTS_API_URL,
    NYC_CITYGML_ARCHIVE_URL,
    NYC_DEM_DATASET_URL,
    NYC_LIDAR_DATASET_URL,
    NYC_PLUTO_API_URL,
    build_asset_manifest,
    build_enriched_footprint_geojson,
    ensure_citygml_archive,
    fetch_building_footprints_for_bbls,
    fetch_pluto_records_for_bbox,
    load_citygml,
    load_footprints,
    metadata_row,
    require_local_asset,
)
from .models import (
    BoundingBox,
    BuildingFeature,
    ExportTarget,
    StudyAreaAssetManifest,
)

__all__ = [
    "DEFAULT_STUDY_AREAS",
    "build_study_area_manifest",
    "export_citygml_geojson",
    "export_citygml_geoparquet",
    "extract_citygml_buildings",
    "extract_manifest_buildings",
]

DEFAULT_STUDY_AREAS = {
    "lower-manhattan-skyline": BoundingBox(
        min_lat=40.7035,
        min_lon=-74.0185,
        max_lat=40.7178,
        max_lon=-73.9975,
    ),
    "empire-state-building": BoundingBox(
        min_lat=40.7445,
        min_lon=-73.9899,
        max_lat=40.7502,
        max_lon=-73.9839,
    ),
}


def extract_citygml_buildings(
    source: str | Path,
    *,
    bbox: BoundingBox | None = None,
) -> tuple[BuildingFeature, ...]:
    """Load local or archived CityGML, extract buildings, and optionally clip."""

    dataset = load_citygml(source)
    buildings = extract_buildings(dataset)
    return clip_to_bbox(buildings, bbox) if bbox is not None else buildings


def build_study_area_manifest(
    *,
    study_area_name: str,
    bbox: BoundingBox,
    cache_dir: str | Path,
    citygml_path: str | Path | None = None,
    allow_citygml_download: bool = False,
    dem_path: str | Path | None = None,
    lidar_path: str | Path | None = None,
) -> StudyAreaAssetManifest:
    """Prepare official cache assets for one mesh study area."""

    cache_root = Path(cache_dir).expanduser().resolve()
    cache_root.mkdir(parents=True, exist_ok=True)

    if citygml_path is not None:
        citygml_source = require_local_asset(
            citygml_path,
            label="CityGML source",
            source_url=NYC_CITYGML_ARCHIVE_URL,
        )
        citygml_metadata = metadata_row(
            name="citygml_source",
            source_url=NYC_CITYGML_ARCHIVE_URL,
            cache_path=citygml_source,
            record_count=1,
            notes="User-staged official CityGML source.",
        )
    elif allow_citygml_download:
        citygml_source = ensure_citygml_archive(cache_root / "DA_WISE_GML.zip")
        citygml_metadata = metadata_row(
            name="citygml_source",
            source_url=NYC_CITYGML_ARCHIVE_URL,
            cache_path=citygml_source,
            record_count=1,
            notes="Downloaded official CityGML archive.",
        )
    else:
        citygml_source = require_local_asset(
            None,
            label="CityGML source",
            source_url=NYC_CITYGML_ARCHIVE_URL,
        )
        citygml_metadata = metadata_row(
            name="citygml_source",
            source_url=NYC_CITYGML_ARCHIVE_URL,
            cache_path=citygml_source,
            record_count=1,
        )

    pluto_rows = fetch_pluto_records_for_bbox(bbox)
    pluto_path = cache_root / "pluto.json"
    pluto_path.write_text(f"{json.dumps(pluto_rows, indent=2)}\n", encoding="utf-8")
    pluto_metadata = metadata_row(
        name="pluto_rows",
        source_url=NYC_PLUTO_API_URL,
        cache_path=pluto_path,
        record_count=len(pluto_rows),
        notes="Filtered to the requested study-area bbox.",
    )

    bbls = tuple(
        str(row.get("bbl", "")).split(".", maxsplit=1)[0]
        for row in pluto_rows
        if row.get("bbl")
    )
    footprint_rows = fetch_building_footprints_for_bbls(bbls)
    footprints_payload = build_enriched_footprint_geojson(footprint_rows, pluto_rows)
    footprints_path = cache_root / "footprints.geojson"
    footprints_path.write_text(
        f"{json.dumps(footprints_payload, indent=2)}\n",
        encoding="utf-8",
    )
    footprints_metadata = metadata_row(
        name="building_footprints",
        source_url=NYC_BUILDING_FOOTPRINTS_API_URL,
        cache_path=footprints_path,
        record_count=len(footprints_payload["features"]),
        notes="Fetched by BBL after PLUTO bbox selection.",
    )

    dem_source = (
        None
        if dem_path is None
        else require_local_asset(
            dem_path,
            label="DEM source",
            source_url=NYC_DEM_DATASET_URL,
        )
    )
    lidar_source = (
        None
        if lidar_path is None
        else require_local_asset(
            lidar_path,
            label="LiDAR source",
            source_url=NYC_LIDAR_DATASET_URL,
        )
    )

    metadata = [citygml_metadata, pluto_metadata, footprints_metadata]
    if dem_source is not None:
        metadata.append(
            metadata_row(
                name="dem_source",
                source_url=NYC_DEM_DATASET_URL,
                cache_path=dem_source,
                record_count=1,
                notes="User-staged official DEM source.",
            )
        )
    if lidar_source is not None:
        metadata.append(
            metadata_row(
                name="lidar_source",
                source_url=NYC_LIDAR_DATASET_URL,
                cache_path=lidar_source,
                record_count=1,
                notes="User-staged official LiDAR source.",
            )
        )

    manifest = build_asset_manifest(
        study_area_name=study_area_name,
        bbox=bbox,
        cache_dir=cache_root,
        citygml_source=citygml_source,
        metadata=tuple(metadata),
        footprints_source=footprints_path,
        pluto_source=pluto_path,
        dem_source=dem_source,
        lidar_source=lidar_source,
    )
    manifest_path = cache_root / "asset-manifest.json"
    manifest_payload = {
        "study_area_name": manifest.study_area_name,
        "bbox": {
            "min_lat": manifest.bbox.min_lat,
            "min_lon": manifest.bbox.min_lon,
            "max_lat": manifest.bbox.max_lat,
            "max_lon": manifest.bbox.max_lon,
        },
        "citygml_source": str(manifest.citygml_source),
        "footprints_source": None
        if manifest.footprints_source is None
        else str(manifest.footprints_source),
        "pluto_source": None if manifest.pluto_source is None else str(manifest.pluto_source),
        "dem_source": None if manifest.dem_source is None else str(manifest.dem_source),
        "lidar_source": None if manifest.lidar_source is None else str(manifest.lidar_source),
        "sources": [
            {
                "name": item.name,
                "source_url": item.source_url,
                "cache_path": str(item.cache_path),
                "refreshed_at": item.refreshed_at.isoformat(),
                "record_count": item.record_count,
                "notes": item.notes,
            }
            for item in manifest.metadata
        ],
    }
    manifest_path.write_text(
        f"{json.dumps(manifest_payload, indent=2)}\n",
        encoding="utf-8",
    )
    return manifest


def extract_manifest_buildings(
    manifest: StudyAreaAssetManifest,
) -> tuple[BuildingFeature, ...]:
    """Load, clip, and enrich buildings for a prepared study-area manifest."""

    buildings = extract_citygml_buildings(manifest.citygml_source, bbox=manifest.bbox)
    if manifest.footprints_source is None:
        return buildings
    return join_pluto(buildings, load_footprints(manifest.footprints_source))


def export_citygml_geojson(
    source: str | Path,
    output_path: str | Path,
    *,
    bbox: BoundingBox | None = None,
) -> Path:
    """Run the CityGML happy path and write GeoJSON."""

    buildings = extract_citygml_buildings(source, bbox=bbox)
    target = ExportTarget(format="geojson", output_path=Path(output_path).expanduser())
    return export_geojson(buildings, target)


def export_citygml_geoparquet(
    source: str | Path,
    output_path: str | Path,
    *,
    bbox: BoundingBox | None = None,
) -> Path:
    """Run the CityGML happy path and write GeoParquet."""

    buildings = extract_citygml_buildings(source, bbox=bbox)
    target = ExportTarget(format="geoparquet", output_path=Path(output_path).expanduser())
    return export_geoparquet(buildings, target)
