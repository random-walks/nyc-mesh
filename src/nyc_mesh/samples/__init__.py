"""Packaged sample data for ``nyc-mesh``."""

from __future__ import annotations

from ._loaders import DEFAULT_SAMPLE_CITYGML, load_sample_citygml

__all__ = [
    "DEFAULT_SAMPLE_CITYGML",
    "load_sample_citygml",
]
