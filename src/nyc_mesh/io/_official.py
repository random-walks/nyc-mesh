"""Official NYC open-data fetch helpers for ``nyc-mesh``."""

from __future__ import annotations

import json
from datetime import UTC, datetime
from pathlib import Path
from typing import Any
from urllib.parse import quote
from urllib.request import urlopen

from ..models import BoundingBox, DataSourceMetadata, StudyAreaAssetManifest

NYC_CITYGML_ARCHIVE_URL = "https://maps.nyc.gov/download/3dmodel/DA_WISE_GML.zip"
NYC_BUILDING_FOOTPRINTS_API_URL = (
    "https://data.cityofnewyork.us/resource/5zhs-2jue.json"
)
NYC_PLUTO_API_URL = "https://data.cityofnewyork.us/resource/64uk-42ks.json"
NYC_DEM_DATASET_URL = "https://data.cityofnewyork.us/City-Government/1-foot-Digital-Elevation-Model-DEM-/dpc8-z3jc/data?no_mobile=true"
NYC_LIDAR_DATASET_URL = (
    "https://noaa-nos-coastal-lidar-pds.s3.amazonaws.com/laz/geoid18/9306/index.html"
)


def _read_json(url: str) -> list[dict[str, Any]]:
    with urlopen(url, timeout=60.0) as response:
        payload = json.loads(response.read().decode("utf-8"))
    if not isinstance(payload, list):
        message = f"Expected a JSON list from {url!r}."
        raise TypeError(message)
    return [row for row in payload if isinstance(row, dict)]


def _build_socrata_url(
    base_url: str,
    *,
    where: str | None = None,
    limit: int = 5000,
    offset: int = 0,
) -> str:
    parts = [f"$limit={limit}", f"$offset={offset}"]
    if where:
        parts.append("$where=" + quote(where, safe="'(),.*_<>="))
    separator = "&" if "?" in base_url else "?"
    return f"{base_url}{separator}{'&'.join(parts)}"


def _fetch_paginated(
    base_url: str,
    *,
    where: str | None = None,
    page_size: int = 5000,
) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    offset = 0
    while True:
        page = _read_json(
            _build_socrata_url(base_url, where=where, limit=page_size, offset=offset)
        )
        rows.extend(page)
        if len(page) < page_size:
            break
        offset += page_size
    return rows


def _normalize_bbl(raw_value: object) -> str:
    text = str(raw_value).strip()
    return text.split(".", maxsplit=1)[0]


def fetch_pluto_records_for_bbox(
    bbox: BoundingBox,
    *,
    page_size: int = 5000,
) -> list[dict[str, Any]]:
    """Fetch PLUTO rows whose centroid falls inside the requested bbox."""

    where = (
        f"latitude >= {bbox.min_lat} and latitude <= {bbox.max_lat} and "
        f"longitude >= {bbox.min_lon} and longitude <= {bbox.max_lon}"
    )
    return _fetch_paginated(NYC_PLUTO_API_URL, where=where, page_size=page_size)


def fetch_building_footprints_for_bbls(
    bbls: tuple[str, ...],
    *,
    page_size: int = 5000,
) -> list[dict[str, Any]]:
    """Fetch official building-footprint rows for the supplied BBL set."""

    normalized_bbls = tuple(sorted({_normalize_bbl(value) for value in bbls if value}))
    if not normalized_bbls:
        return []
    joined = ", ".join(f"'{value}'" for value in normalized_bbls)
    where = f"mappluto_bbl in ({joined}) or base_bbl in ({joined})"
    return _fetch_paginated(
        NYC_BUILDING_FOOTPRINTS_API_URL,
        where=where,
        page_size=page_size,
    )


def ensure_citygml_archive(
    target_path: Path,
    *,
    refresh: bool = False,
    source_url: str = NYC_CITYGML_ARCHIVE_URL,
) -> Path:
    """Download the official CityGML archive when explicitly requested."""

    if target_path.exists() and not refresh:
        return target_path
    target_path.parent.mkdir(parents=True, exist_ok=True)
    with urlopen(source_url, timeout=120.0) as response:
        target_path.write_bytes(response.read())
    return target_path


def require_local_asset(
    provided_path: str | Path | None,
    *,
    label: str,
    source_url: str,
) -> Path:
    """Resolve a user-staged official asset or raise with download guidance."""

    if provided_path is None:
        message = (
            f"{label} must be staged locally for this workflow. Download it from "
            f"{source_url} and pass the local path."
        )
        raise FileNotFoundError(message)
    path = Path(provided_path).expanduser().resolve()
    if not path.exists():
        message = f"{label} does not exist: {path}"
        raise FileNotFoundError(message)
    return path


def build_enriched_footprint_geojson(
    footprint_rows: list[dict[str, Any]],
    pluto_rows: list[dict[str, Any]],
) -> dict[str, Any]:
    """Merge PLUTO attributes into official building-footprint features."""

    pluto_by_bbl = {
        _normalize_bbl(row.get("bbl")): row
        for row in pluto_rows
        if row.get("bbl") is not None
    }
    features = []
    for row in footprint_rows:
        geometry = row.get("the_geom")
        if not isinstance(geometry, dict):
            continue
        bbl = _normalize_bbl(row.get("mappluto_bbl") or row.get("base_bbl") or "")
        pluto = pluto_by_bbl.get(bbl, {})
        properties = {
            "building_id": str(row.get("bin") or row.get("doitt_id") or bbl),
            "bin": str(row.get("bin") or ""),
            "bbl": bbl,
            "base_bbl": str(row.get("base_bbl") or ""),
            "mappluto_bbl": str(row.get("mappluto_bbl") or ""),
            "height_roof": row.get("height_roof"),
            "ground_elevation": row.get("ground_elevation"),
            "construction_year": row.get("construction_year"),
            "address": str(pluto.get("address") or ""),
            "borough": str(pluto.get("borough") or ""),
            "landuse": str(pluto.get("landuse") or ""),
            "ownername": str(pluto.get("ownername") or ""),
            "yearbuilt": str(pluto.get("yearbuilt") or ""),
            "numfloors": str(pluto.get("numfloors") or ""),
            "zipcode": str(pluto.get("zipcode") or ""),
        }
        features.append(
            {
                "type": "Feature",
                "id": properties["building_id"],
                "properties": properties,
                "geometry": geometry,
            }
        )
    return {"type": "FeatureCollection", "features": features}


def build_asset_manifest(
    *,
    study_area_name: str,
    bbox: BoundingBox,
    cache_dir: Path,
    citygml_source: Path,
    metadata: tuple[DataSourceMetadata, ...],
    footprints_source: Path | None = None,
    pluto_source: Path | None = None,
    dem_source: Path | None = None,
    lidar_source: Path | None = None,
) -> StudyAreaAssetManifest:
    """Build a typed manifest for one official mesh study area."""

    return StudyAreaAssetManifest(
        study_area_name=study_area_name,
        bbox=bbox,
        cache_dir=cache_dir,
        citygml_source=citygml_source,
        metadata=metadata,
        footprints_source=footprints_source,
        pluto_source=pluto_source,
        dem_source=dem_source,
        lidar_source=lidar_source,
    )


def metadata_row(
    *,
    name: str,
    source_url: str,
    cache_path: Path,
    record_count: int,
    notes: str = "",
) -> DataSourceMetadata:
    """Create a metadata row timestamped at the current UTC time."""

    return DataSourceMetadata(
        name=name,
        source_url=source_url,
        cache_path=cache_path,
        refreshed_at=datetime.now(tz=UTC),
        record_count=record_count,
        notes=notes,
    )
