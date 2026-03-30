"""Planned processing steps for transforming raw NYC 3D inputs."""

from __future__ import annotations

from typing import Any

from ._not_implemented import planned_surface
from .models import BoundingBox


def extract_buildings(citygml_data: Any) -> Any:
    """Extract footprints and measured heights from loaded building data."""
    planned_surface("extract_buildings()")


def clip_to_bbox(data: Any, bbox: BoundingBox) -> Any:
    """Clip a loaded or processed dataset to a geographic bounding box."""
    planned_surface("clip_to_bbox()")


def join_pluto(buildings: Any, pluto_data: Any) -> Any:
    """Join optional PLUTO tax lot attributes onto extracted buildings."""
    planned_surface("join_pluto()")


def generate_terrain_mesh(lidar_or_dem_data: Any) -> Any:
    """Generate a lightweight terrain mesh from elevation inputs."""
    planned_surface("generate_terrain_mesh()")
