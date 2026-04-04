"""Typed models for the refactored ``nyc-mesh`` package."""

from __future__ import annotations

from dataclasses import dataclass, field, replace
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from pathlib import Path

Coordinate2D = tuple[float, float]
Coordinate3D = tuple[float, float, float]
ScalarValue = str | int | float | None


@dataclass(frozen=True, slots=True)
class BoundingBox:
    """Geographic clipping bounds in WGS84 order."""

    min_lat: float
    min_lon: float
    max_lat: float
    max_lon: float

    def __post_init__(self) -> None:
        if self.min_lat >= self.max_lat:
            message = "BoundingBox.min_lat must be smaller than max_lat."
            raise ValueError(message)
        if self.min_lon >= self.max_lon:
            message = "BoundingBox.min_lon must be smaller than max_lon."
            raise ValueError(message)

    def contains(self, longitude: float, latitude: float) -> bool:
        """Return whether the WGS84 point falls inside the bounding box."""

        return (
            self.min_lon <= longitude <= self.max_lon
            and self.min_lat <= latitude <= self.max_lat
        )


@dataclass(frozen=True, slots=True)
class ExportTarget:
    """Destination metadata for export commands."""

    format: str
    output_path: Path


@dataclass(frozen=True, slots=True)
class NeighborhoodRequest:
    """A named extraction request for a neighborhood-scale clip."""

    name: str
    bbox: BoundingBox


@dataclass(frozen=True, slots=True)
class CityGMLBuilding:
    """Single CityGML building with an EPSG:2263 footprint and optional height."""

    building_id: str
    footprint_2263: tuple[Coordinate2D, ...]
    measured_height: float | None


@dataclass(frozen=True, slots=True)
class CityGMLDataset:
    """Loaded local CityGML source and parsed building records."""

    source: Path
    buildings: tuple[CityGMLBuilding, ...]


@dataclass(frozen=True, slots=True)
class BuildingFeature:
    """Height-aware building feature reprojected to WGS84 coordinates."""

    building_id: str
    footprint_4326: tuple[Coordinate2D, ...]
    height: float
    properties: dict[str, ScalarValue] = field(default_factory=dict)

    @property
    def centroid(self) -> Coordinate2D:
        """Return the simple polygon-centroid average."""

        ring = self.footprint_4326[:-1] if self.footprint_4326 else ()
        if not ring:
            return (0.0, 0.0)
        return (
            sum(point[0] for point in ring) / len(ring),
            sum(point[1] for point in ring) / len(ring),
        )

    def with_properties(self, updates: dict[str, ScalarValue]) -> BuildingFeature:
        """Return a copy with merged properties."""

        merged = {**self.properties, **updates}
        return replace(self, properties=merged)


@dataclass(frozen=True, slots=True)
class FootprintFeature:
    """Generic polygon feature loaded from GeoJSON or shapefile footprints."""

    feature_id: str
    footprint_4326: tuple[Coordinate2D, ...]
    properties: dict[str, ScalarValue] = field(default_factory=dict)

    @property
    def centroid(self) -> Coordinate2D:
        ring = self.footprint_4326[:-1] if self.footprint_4326 else ()
        if not ring:
            return (0.0, 0.0)
        return (
            sum(point[0] for point in ring) / len(ring),
            sum(point[1] for point in ring) / len(ring),
        )


@dataclass(frozen=True, slots=True)
class FootprintDataset:
    """Loaded footprint features used for PLUTO-style joins."""

    source: Path
    features: tuple[FootprintFeature, ...]


@dataclass(frozen=True, slots=True)
class LidarPoint:
    """Single LiDAR point."""

    x: float
    y: float
    z: float
    intensity: int | None = None


@dataclass(frozen=True, slots=True)
class LidarDataset:
    """Loaded LiDAR point cloud."""

    source: Path
    points: tuple[LidarPoint, ...]


@dataclass(frozen=True, slots=True)
class DEMDataset:
    """Loaded digital elevation model."""

    source: Path
    values: tuple[tuple[float | None, ...], ...]
    origin_x: float
    origin_y: float
    cell_size: float
    nodata: float | None
    crs: str

    @property
    def rows(self) -> int:
        return len(self.values)

    @property
    def cols(self) -> int:
        return len(self.values[0]) if self.values else 0


@dataclass(frozen=True, slots=True)
class TerrainMeshDataset:
    """Triangulated terrain mesh."""

    source: str
    vertices: tuple[Coordinate3D, ...]
    triangles: tuple[tuple[int, int, int], ...]
