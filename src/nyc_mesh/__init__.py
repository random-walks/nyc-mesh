"""Top-level package for the planned ``nyc-mesh`` API surface.

The repository is intentionally seeded with typed placeholders so contributors
can see the target shape of the library before the implementation lands.
"""

from __future__ import annotations

try:
    from ._version import version as __version__
except ImportError:  # pragma: no cover - fallback for editable installs
    __version__ = "0+unknown"

from .cli import main
from .exporters import export_3d_tiles, export_geojson, export_geoparquet, export_gltf
from .loaders import load_citygml, load_dem, load_footprints, load_lidar
from .models import (
    BoundingBox,
    BuildingFeature,
    CityGMLBuilding,
    CityGMLDataset,
    ExportTarget,
    NeighborhoodRequest,
)
from .processors import (
    clip_to_bbox,
    extract_buildings,
    generate_terrain_mesh,
    join_pluto,
)

__all__ = [
    "BoundingBox",
    "BuildingFeature",
    "CityGMLBuilding",
    "CityGMLDataset",
    "ExportTarget",
    "NeighborhoodRequest",
    "__version__",
    "clip_to_bbox",
    "export_3d_tiles",
    "export_geojson",
    "export_geoparquet",
    "export_gltf",
    "extract_buildings",
    "generate_terrain_mesh",
    "join_pluto",
    "load_citygml",
    "load_dem",
    "load_footprints",
    "load_lidar",
    "main",
]
