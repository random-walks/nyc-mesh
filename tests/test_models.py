from __future__ import annotations

import importlib.metadata

import pytest

import nyc_mesh
from nyc_mesh.models import BoundingBox


def test_root_namespace_only_exports_version() -> None:
    assert nyc_mesh.__all__ == ["__version__"]
    assert importlib.metadata.version("nyc-mesh") == nyc_mesh.__version__


def test_bounding_box_validates_coordinate_order() -> None:
    with pytest.raises(ValueError, match="min_lat"):
        BoundingBox(min_lat=40.71, min_lon=-74.01, max_lat=40.70, max_lon=-74.0)
