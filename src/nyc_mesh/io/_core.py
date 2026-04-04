"""Loader entry points for raw ``nyc-mesh`` source data."""

from __future__ import annotations

import csv
import json
import zipfile
from io import BytesIO
from pathlib import Path
from typing import Any, cast

from lxml import etree

from ..models import (
    CityGMLBuilding,
    CityGMLDataset,
    Coordinate2D,
    DEMDataset,
    FootprintDataset,
    FootprintFeature,
    LidarDataset,
    LidarPoint,
)
from ._geo import normalise_ring, project_ring_to_wgs84

try:  # pragma: no cover - exercised when dependency is installed
    import laspy
except ImportError:  # pragma: no cover - fallback for environments without laspy
    laspy = None

try:  # pragma: no cover - exercised when dependency is installed
    import rasterio
    from rasterio.io import MemoryFile
except ImportError:  # pragma: no cover - fallback for environments without rasterio
    rasterio = None
    MemoryFile = None

try:  # pragma: no cover - exercised when dependency is installed
    import shapefile
except ImportError:  # pragma: no cover - fallback for environments without pyshp
    shapefile = None

_NS = {
    "bldg": "http://www.opengis.net/citygml/building/2.0",
    "gml": "http://www.opengis.net/gml",
}
_GML_ID = "{http://www.opengis.net/gml}id"


def _zip_members(source_path: Path, *, suffixes: tuple[str, ...]) -> tuple[str, bytes]:
    with zipfile.ZipFile(source_path) as archive:
        for member_name in archive.namelist():
            if member_name.lower().endswith(suffixes):
                return member_name, archive.read(member_name)
    message = f"{source_path} does not contain a member ending with {suffixes!r}."
    raise ValueError(message)


def _parse_float_values(raw_values: str) -> tuple[float, ...]:
    return tuple(float(value) for value in raw_values.split())


def _ring_from_pos_list(polygon: Any, ring: Any) -> tuple[Coordinate2D, ...]:
    pos_list_nodes = cast(
        "list[etree._Element]",
        ring.xpath("./gml:posList", namespaces=_NS),
    )
    if not pos_list_nodes:
        return ()

    pos_list = pos_list_nodes[0]
    raw_text = (pos_list.text or "").strip()
    if not raw_text:
        return ()

    values = _parse_float_values(raw_text)
    if len(values) < 6:
        return ()

    srs_dimension_raw = (
        pos_list.get("srsDimension")
        or ring.get("srsDimension")
        or polygon.get("srsDimension")
        or ""
    )
    srs_dimension = int(srs_dimension_raw) if srs_dimension_raw.isdigit() else 0
    dimension = (
        srs_dimension if srs_dimension in {2, 3} else 3 if len(values) % 3 == 0 else 2
    )
    if len(values) % dimension != 0:
        message = "Invalid CityGML ring coordinate count in gml:posList."
        raise ValueError(message)
    coords = [
        (values[index], values[index + 1]) for index in range(0, len(values), dimension)
    ]
    return normalise_ring(tuple(coords))


def _ring_from_pos_nodes(ring: Any) -> tuple[Coordinate2D, ...]:
    coords: list[Coordinate2D] = []
    for pos_node in cast(
        "list[etree._Element]",
        ring.xpath("./gml:pos", namespaces=_NS),
    ):
        raw_text = (pos_node.text or "").strip()
        if not raw_text:
            continue
        values = _parse_float_values(raw_text)
        if len(values) < 2:
            continue
        coords.append((values[0], values[1]))
    return normalise_ring(tuple(coords))


def _extract_exterior_ring(polygon: Any) -> tuple[Coordinate2D, ...]:
    linear_rings = cast(
        "list[etree._Element]",
        polygon.xpath("./gml:exterior/gml:LinearRing", namespaces=_NS),
    )
    if not linear_rings:
        return ()
    ring = linear_rings[0]
    from_pos_list = _ring_from_pos_list(polygon=polygon, ring=ring)
    if from_pos_list:
        return from_pos_list
    return _ring_from_pos_nodes(ring)


def _extract_measured_height(building: Any) -> float | None:
    height_nodes = cast(
        "list[etree._Element]",
        building.xpath("./bldg:measuredHeight", namespaces=_NS),
    )
    if not height_nodes:
        return None
    raw_value = (height_nodes[0].text or "").strip()
    if not raw_value:
        return None
    try:
        return float(raw_value)
    except ValueError:
        return None


def load_citygml(source: str | Path) -> CityGMLDataset:
    """Load building footprints and measured heights from a local CityGML file."""

    if isinstance(source, str) and source.startswith(("http://", "https://")):
        message = "load_citygml() supports local file paths only."
        raise ValueError(message)

    source_path = Path(source).expanduser()
    if not source_path.exists():
        message = f"CityGML source does not exist: {source_path}"
        raise FileNotFoundError(message)
    if not source_path.is_file():
        message = f"CityGML source must be a file path: {source_path}"
        raise ValueError(message)
    parser = etree.XMLParser(
        resolve_entities=False,
        no_network=True,
        remove_comments=True,
    )
    if source_path.suffix.lower() == ".zip":
        _, member_bytes = _zip_members(source_path, suffixes=(".gml", ".xml"))
        root = etree.fromstring(member_bytes, parser=parser)
    else:
        root = etree.parse(str(source_path), parser=parser).getroot()

    buildings: list[CityGMLBuilding] = []
    for building_node in cast(
        "list[etree._Element]",
        root.xpath(".//bldg:Building", namespaces=_NS),
    ):
        footprint_2263: tuple[Coordinate2D, ...] = ()
        for polygon in cast(
            "list[etree._Element]",
            building_node.xpath(".//gml:Polygon", namespaces=_NS),
        ):
            footprint_2263 = _extract_exterior_ring(polygon)
            if footprint_2263:
                break
        if not footprint_2263:
            continue
        buildings.append(
            CityGMLBuilding(
                building_id=building_node.get(_GML_ID)
                or f"building-{len(buildings) + 1}",
                footprint_2263=footprint_2263,
                measured_height=_extract_measured_height(building_node),
            )
        )
    return CityGMLDataset(source=source_path.resolve(), buildings=tuple(buildings))


def _load_xyz_text(source_path: Path) -> tuple[LidarPoint, ...]:
    text = source_path.read_text(encoding="utf-8")
    lines = [line.strip() for line in text.splitlines() if line.strip()]
    if not lines:
        return ()

    header = lines[0].lower().replace(",", " ").split()
    if {"x", "y", "z"}.issubset(header):
        reader = csv.DictReader(lines)
        return tuple(
            LidarPoint(
                x=float(row["x"]),
                y=float(row["y"]),
                z=float(row["z"]),
                intensity=None if not row.get("intensity") else int(row["intensity"]),
            )
            for row in reader
        )

    points = []
    for line in lines:
        parts = line.replace(",", " ").split()
        if len(parts) < 3:
            continue
        points.append(
            LidarPoint(x=float(parts[0]), y=float(parts[1]), z=float(parts[2]))
        )
    return tuple(points)


def load_lidar(source: str | Path) -> LidarDataset:
    """Load LiDAR point data from LAS/LAZ, CSV, XYZ, or JSON inputs."""

    source_path = Path(source).expanduser()
    if not source_path.exists():
        message = f"LiDAR source does not exist: {source_path}"
        raise FileNotFoundError(message)

    suffix = source_path.suffix.lower()
    if suffix == ".zip":
        if laspy is None:
            message = (
                "ZIP-wrapped LAS/LAZ loading requires the optional `laspy` dependency."
            )
            raise RuntimeError(message)
        _, member_bytes = _zip_members(source_path, suffixes=(".las", ".laz"))
        las = laspy.read(BytesIO(member_bytes))
        points = tuple(
            LidarPoint(
                x=float(x_coord),
                y=float(y_coord),
                z=float(z_coord),
                intensity=None if las.intensity is None else int(las.intensity[index]),
            )
            for index, (x_coord, y_coord, z_coord) in enumerate(
                zip(las.x, las.y, las.z, strict=True)
            )
        )
        return LidarDataset(source=source_path.resolve(), points=points)
    if suffix in {".las", ".laz"}:
        if laspy is None:
            message = "LAS/LAZ loading requires the optional `laspy` dependency."
            raise RuntimeError(message)
        las = laspy.read(source_path)
        points = tuple(
            LidarPoint(
                x=float(x_coord),
                y=float(y_coord),
                z=float(z_coord),
                intensity=None if las.intensity is None else int(las.intensity[index]),
            )
            for index, (x_coord, y_coord, z_coord) in enumerate(
                zip(las.x, las.y, las.z, strict=True)
            )
        )
        return LidarDataset(source=source_path.resolve(), points=points)

    if suffix in {".csv", ".xyz", ".txt"}:
        return LidarDataset(
            source=source_path.resolve(),
            points=_load_xyz_text(source_path),
        )

    if suffix == ".json":
        payload = json.loads(source_path.read_text(encoding="utf-8"))
        raw_points = payload.get("points") if isinstance(payload, dict) else payload
        if not isinstance(raw_points, list):
            message = f"{source_path} must contain a list of points."
            raise TypeError(message)
        points = tuple(
            LidarPoint(
                x=float(point["x"]),
                y=float(point["y"]),
                z=float(point["z"]),
                intensity=None
                if point.get("intensity") is None
                else int(point["intensity"]),
            )
            for point in raw_points
            if isinstance(point, dict)
        )
        return LidarDataset(source=source_path.resolve(), points=points)

    message = f"Unsupported LiDAR format: {source_path.suffix}"
    raise ValueError(message)


def load_dem(source: str | Path) -> DEMDataset:
    """Load a DEM from ESRI ASCII grid or JSON grid data."""

    source_path = Path(source).expanduser()
    if not source_path.exists():
        message = f"DEM source does not exist: {source_path}"
        raise FileNotFoundError(message)

    suffix = source_path.suffix.lower()
    if suffix == ".zip":
        member_name, member_bytes = _zip_members(
            source_path, suffixes=(".tif", ".tiff", ".asc")
        )
        member_suffix = Path(member_name).suffix.lower()
        if member_suffix in {".tif", ".tiff"}:
            if rasterio is None or MemoryFile is None:
                message = (
                    "GeoTIFF DEM loading requires the optional `rasterio` dependency."
                )
                raise RuntimeError(message)
            with MemoryFile(member_bytes) as memory_file, memory_file.open() as dataset:
                return _dem_from_rasterio(dataset, source_path)
        return _dem_from_ascii_text(member_bytes.decode("utf-8"), source_path)

    if suffix in {".tif", ".tiff"}:
        if rasterio is None:
            message = "GeoTIFF DEM loading requires the optional `rasterio` dependency."
            raise RuntimeError(message)
        with rasterio.open(source_path) as dataset:
            return _dem_from_rasterio(dataset, source_path)
    if suffix == ".json":
        payload = json.loads(source_path.read_text(encoding="utf-8"))
        values = tuple(
            tuple(None if value is None else float(value) for value in row)
            for row in payload["values"]
        )
        return DEMDataset(
            source=source_path.resolve(),
            values=values,
            origin_x=float(payload["origin_x"]),
            origin_y=float(payload["origin_y"]),
            cell_size=float(payload["cell_size"]),
            nodata=None if payload.get("nodata") is None else float(payload["nodata"]),
            crs=str(payload.get("crs", "EPSG:2263")),
        )

    if suffix != ".asc":
        message = f"Unsupported DEM format: {source_path.suffix}"
        raise ValueError(message)
    return _dem_from_ascii_text(source_path.read_text(encoding="utf-8"), source_path)


def _dem_from_ascii_text(raw_text: str, source_path: Path) -> DEMDataset:
    lines = [line.strip() for line in raw_text.splitlines() if line.strip()]
    header: dict[str, str] = {}
    for line in lines[:6]:
        key, value = line.split(maxsplit=1)
        header[key.lower()] = value

    ncols = int(header["ncols"])
    nrows = int(header["nrows"])
    origin_x = float(header.get("xllcorner", header.get("xllcenter", "0")))
    origin_y = float(header.get("yllcorner", header.get("yllcenter", "0")))
    cell_size = float(header["cellsize"])
    nodata = float(header["nodata_value"]) if "nodata_value" in header else None

    grid_rows = []
    for line in lines[6:]:
        row = []
        for token in line.split():
            numeric = float(token)
            row.append(None if nodata is not None and numeric == nodata else numeric)
        grid_rows.append(tuple(row))
    if len(grid_rows) != nrows or any(len(row) != ncols for row in grid_rows):
        message = f"{source_path} DEM dimensions do not match its header."
        raise ValueError(message)
    return DEMDataset(
        source=source_path.resolve(),
        values=tuple(grid_rows),
        origin_x=origin_x,
        origin_y=origin_y,
        cell_size=cell_size,
        nodata=nodata,
        crs="EPSG:2263",
    )


def _dem_from_rasterio(dataset: Any, source_path: Path) -> DEMDataset:
    band = dataset.read(1)
    nodata = dataset.nodata
    values = tuple(
        tuple(
            None
            if nodata is not None and float(value) == float(nodata)
            else float(value)
            for value in row
        )
        for row in band
    )
    transform = dataset.transform
    return DEMDataset(
        source=source_path.resolve(),
        values=values,
        origin_x=float(transform.c),
        origin_y=float(transform.f),
        cell_size=float(transform.a),
        nodata=None if nodata is None else float(nodata),
        crs=str(dataset.crs or "EPSG:2263"),
    )


def _coerce_geojson_ring(raw_coordinates: list[Any]) -> tuple[Coordinate2D, ...]:
    ring = tuple(
        (float(point[0]), float(point[1]))
        for point in raw_coordinates
        if len(point) >= 2
    )
    normalized = normalise_ring(ring)
    if not normalized:
        return ()
    first_lon, first_lat = normalized[0]
    if abs(first_lon) > 180 or abs(first_lat) > 90:
        return project_ring_to_wgs84(normalized)
    return normalized


def _coerce_geojson_footprint(geometry: dict[str, Any]) -> tuple[Coordinate2D, ...]:
    geometry_type = geometry.get("type")
    coordinates = geometry.get("coordinates")
    if not isinstance(coordinates, list) or not coordinates:
        return ()
    if geometry_type == "Polygon":
        first_ring = coordinates[0]
        return _coerce_geojson_ring(first_ring) if isinstance(first_ring, list) else ()
    if geometry_type == "MultiPolygon":
        first_polygon = coordinates[0]
        if isinstance(first_polygon, list) and first_polygon:
            first_ring = first_polygon[0]
            return (
                _coerce_geojson_ring(first_ring) if isinstance(first_ring, list) else ()
            )
    return ()


def load_footprints(source: str | Path) -> FootprintDataset:
    """Load footprint polygons from GeoJSON or ESRI shapefile sources."""

    source_path = Path(source).expanduser()
    if not source_path.exists():
        message = f"Footprint source does not exist: {source_path}"
        raise FileNotFoundError(message)

    suffix = source_path.suffix.lower()
    if suffix in {".geojson", ".json"}:
        payload = json.loads(source_path.read_text(encoding="utf-8"))
        features = payload.get("features")
        if not isinstance(features, list):
            message = f"{source_path} must contain a GeoJSON FeatureCollection."
            raise TypeError(message)
        loaded = []
        for index, feature in enumerate(features, start=1):
            if not isinstance(feature, dict):
                continue
            geometry = feature.get("geometry")
            properties = feature.get("properties", {})
            if not isinstance(geometry, dict):
                continue
            ring = _coerce_geojson_footprint(geometry)
            if not ring:
                continue
            feature_id = str(
                properties.get("building_id")
                or properties.get("bbl")
                or feature.get("id")
                or f"feature-{index}"
            )
            loaded.append(
                FootprintFeature(
                    feature_id=feature_id,
                    footprint_4326=ring,
                    properties={
                        str(key): value
                        for key, value in properties.items()
                        if isinstance(value, (str, int, float)) or value is None
                    },
                )
            )
        return FootprintDataset(source=source_path.resolve(), features=tuple(loaded))

    if suffix == ".shp":
        if shapefile is None:
            message = "Shapefile loading requires the optional `pyshp` dependency."
            raise RuntimeError(message)
        reader = shapefile.Reader(str(source_path))
        field_names = [
            field[0] for field in reader.fields if field[0] != "DeletionFlag"
        ]
        loaded = []
        for index, shape_record in enumerate(reader.iterShapeRecords(), start=1):
            if shape_record.shape.shapeTypeName not in {"POLYGON", "POLYGONZ"}:
                continue
            properties = {
                key: value
                for key, value in zip(field_names, shape_record.record, strict=False)
                if isinstance(value, (str, int, float)) or value is None
            }
            ring = normalise_ring(
                tuple(
                    (float(point[0]), float(point[1]))
                    for point in shape_record.shape.points
                )
            )
            if not ring:
                continue
            feature_id = str(
                properties.get("building_id")
                or properties.get("bbl")
                or f"feature-{index}"
            )
            loaded.append(
                FootprintFeature(
                    feature_id=feature_id,
                    footprint_4326=ring,
                    properties=properties,
                )
            )
        return FootprintDataset(source=source_path.resolve(), features=tuple(loaded))

    message = f"Unsupported footprint format: {source_path.suffix}"
    raise ValueError(message)
