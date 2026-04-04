"""Packaged sample-data loaders for ``nyc-mesh``."""

from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING

from ..io import load_citygml

if TYPE_CHECKING:
    from ..models import CityGMLDataset

_SAMPLES_DIRECTORY = Path(__file__).resolve().parent / "data"
DEFAULT_SAMPLE_CITYGML = _SAMPLES_DIRECTORY / "dumbo-sample.gml"


def load_sample_citygml() -> CityGMLDataset:
    """Load the packaged DUMBO-scale sample CityGML file."""

    return load_citygml(DEFAULT_SAMPLE_CITYGML)
