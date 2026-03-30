"""Loader entry points for raw NYC 3D data sources."""

from __future__ import annotations

from pathlib import Path
from typing import Any, cast

from lxml import etree

from ._not_implemented import planned_surface
from .models import CityGMLBuilding, CityGMLDataset, Coordinate2D

_NS = {
    "bldg": "http://www.opengis.net/citygml/building/2.0",
    "gml": "http://www.opengis.net/gml",
}
_GML_ID = "{http://www.opengis.net/gml}id"


def _parse_float_values(raw_values: str) -> tuple[float, ...]:
    return tuple(float(value) for value in raw_values.split())


def _normalise_ring(coords: tuple[Coordinate2D, ...]) -> tuple[Coordinate2D, ...]:
    if len(coords) < 3:
        return ()
    closed_ring = coords if coords[0] == coords[-1] else (*coords, coords[0])
    if len(set(closed_ring[:-1])) < 3:
        return ()
    return closed_ring


def _ring_from_pos_list(polygon: Any, ring: Any) -> tuple[Coordinate2D, ...]:
    pos_list_nodes = cast(
        "list[etree._Element]", ring.xpath("./gml:posList", namespaces=_NS)
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
    dimension = srs_dimension if srs_dimension in {2, 3} else 3 if len(values) % 3 == 0 else 2

    if len(values) % dimension != 0:
        message = "Invalid CityGML ring coordinate count in gml:posList."
        raise ValueError(message)

    coords = [(values[index], values[index + 1]) for index in range(0, len(values), dimension)]
    return _normalise_ring(tuple(coords))


def _ring_from_pos_nodes(ring: Any) -> tuple[Coordinate2D, ...]:
    coords: list[Coordinate2D] = []
    for pos_node in cast("list[etree._Element]", ring.xpath("./gml:pos", namespaces=_NS)):
        raw_text = (pos_node.text or "").strip()
        if not raw_text:
            continue
        values = _parse_float_values(raw_text)
        if len(values) < 2:
            continue
        coords.append((values[0], values[1]))
    return _normalise_ring(tuple(coords))


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
        "list[etree._Element]", building.xpath("./bldg:measuredHeight", namespaces=_NS)
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
    """Load NYC building geometry from a local CityGML file.

    v0.1 intentionally supports local files only.
    """
    if isinstance(source, str) and source.startswith(("http://", "https://")):
        message = "v0.1 load_citygml() supports local file paths only."
        raise ValueError(message)

    source_path = Path(source).expanduser()
    if not source_path.exists():
        message = f"CityGML source does not exist: {source_path}"
        raise FileNotFoundError(message)
    if not source_path.is_file():
        message = f"CityGML source must be a file path: {source_path}"
        raise ValueError(message)
    parser = etree.XMLParser(resolve_entities=False, no_network=True, remove_comments=True)
    root = etree.parse(str(source_path), parser=parser).getroot()

    buildings: list[CityGMLBuilding] = []
    for building_node in cast(
        "list[etree._Element]", root.xpath(".//bldg:Building", namespaces=_NS)
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

        building_id = building_node.get(_GML_ID) or f"building-{len(buildings) + 1}"
        buildings.append(
            CityGMLBuilding(
                building_id=building_id,
                footprint_2263=footprint_2263,
                measured_height=_extract_measured_height(building_node),
            )
        )

    return CityGMLDataset(source=source_path.resolve(), buildings=tuple(buildings))


def load_lidar(_source: str | Path) -> Any:
    """Load NYC LiDAR point cloud data from a local path or URL."""
    planned_surface("load_lidar()")


def load_dem(_source: str | Path) -> Any:
    """Load a raster elevation source used for terrain generation."""
    planned_surface("load_dem()")


def load_footprints(_source: str | Path) -> Any:
    """Load building footprints from GeoJSON, Shapefile, or similar sources."""
    planned_surface("load_footprints()")
