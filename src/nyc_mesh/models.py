"""Typed planning models for the target ``nyc-mesh`` package surface."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class BoundingBox:
    """Geographic clipping bounds in WGS84 order."""

    min_lat: float
    min_lon: float
    max_lat: float
    max_lon: float


@dataclass(frozen=True)
class NeighborhoodRequest:
    """A named extraction request for a neighborhood-scale clip."""

    name: str
    bbox: BoundingBox


@dataclass(frozen=True)
class ExportTarget:
    """Destination metadata for an eventual export command."""

    format: str
    output_path: Path
