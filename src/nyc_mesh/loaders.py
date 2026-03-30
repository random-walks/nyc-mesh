"""Planned loader entry points for raw NYC 3D data sources."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from ._not_implemented import planned_surface


def load_citygml(source: str | Path) -> Any:
    """Load NYC building geometry from a CityGML source."""
    planned_surface("load_citygml()")


def load_lidar(source: str | Path) -> Any:
    """Load NYC LiDAR point cloud data from a local path or URL."""
    planned_surface("load_lidar()")


def load_dem(source: str | Path) -> Any:
    """Load a raster elevation source used for terrain generation."""
    planned_surface("load_dem()")


def load_footprints(source: str | Path) -> Any:
    """Load building footprints from GeoJSON, Shapefile, or similar sources."""
    planned_surface("load_footprints()")
