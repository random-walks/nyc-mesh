"""CLI scaffold for the future ``nyc-mesh`` command."""

from __future__ import annotations

from ._not_implemented import planned_surface


def main(argv: list[str] | None = None) -> int:
    """Entry point for the future command-line interface."""
    del argv
    planned_surface("nyc-mesh CLI")
