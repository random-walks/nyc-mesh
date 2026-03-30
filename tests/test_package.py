from __future__ import annotations

import importlib.metadata

import nyc_mesh as m


def test_version() -> None:
    assert importlib.metadata.version("nyc_mesh") == m.__version__
