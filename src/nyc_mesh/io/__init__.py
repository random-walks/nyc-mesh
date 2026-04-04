"""Public loaders for ``nyc-mesh``."""

from __future__ import annotations

from ._core import (
    load_citygml,
    load_dem,
    load_footprints,
    load_lidar,
)
from ._official import (
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
    metadata_row,
    require_local_asset,
)

__all__ = [
    "NYC_BUILDING_FOOTPRINTS_API_URL",
    "NYC_CITYGML_ARCHIVE_URL",
    "NYC_DEM_DATASET_URL",
    "NYC_LIDAR_DATASET_URL",
    "NYC_PLUTO_API_URL",
    "build_asset_manifest",
    "build_enriched_footprint_geojson",
    "ensure_citygml_archive",
    "fetch_building_footprints_for_bbls",
    "fetch_pluto_records_for_bbox",
    "load_citygml",
    "load_dem",
    "load_footprints",
    "load_lidar",
    "metadata_row",
    "require_local_asset",
]
