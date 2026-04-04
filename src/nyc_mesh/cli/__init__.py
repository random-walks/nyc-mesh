"""Public CLI entry points for ``nyc-mesh``."""

from __future__ import annotations

from ._main import build_parser, main

__all__ = [
    "build_parser",
    "main",
]
