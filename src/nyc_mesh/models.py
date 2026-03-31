"""Typed planning and runtime models for ``nyc-mesh``."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from pathlib import Path

Coordinate2D = tuple[float, float]


@dataclass(frozen=True)
class BoundingBox:
    """Geographic clipping bounds in WGS84 order."""

    min_lat: float
    min_lon: float
    max_lat: float
    max_lon: float


@dataclass(frozen=True)
class CityGMLBuilding:
    """Single CityGML building with an EPSG:2263 footprint and optional height."""

    building_id: str
    footprint_2263: tuple[Coordinate2D, ...]
    measured_height: float | None


@dataclass(frozen=True)
class CityGMLDataset:
    """Loaded local CityGML source and parsed building records."""

    source: Path
    buildings: tuple[CityGMLBuilding, ...]


@dataclass(frozen=True)
class BuildingFeature:
    """Height-aware building feature reprojected to WGS84 coordinates."""

    building_id: str
    footprint_4326: tuple[Coordinate2D, ...]
    height: float


@dataclass(frozen=True)
class NeighborhoodRequest:
    """A named extraction request for a neighborhood-scale clip."""

    name: str
    bbox: BoundingBox


@dataclass(frozen=True)
class ExportTarget:
    """Destination metadata for an implemented or planned export command."""

    format: str
    output_path: Path
