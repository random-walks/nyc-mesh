"""Command-line interface for the implemented ``nyc-mesh`` workflows."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import TYPE_CHECKING, TextIO, cast

from lxml import etree

from ..models import BoundingBox
from ..pipeline import (
    export_citygml_geojson,
    export_citygml_geoparquet,
    extract_citygml_buildings,
)

if TYPE_CHECKING:
    from collections.abc import Callable, Sequence

try:
    from .._version import version as _VERSION
except ImportError:  # pragma: no cover - fallback for editable installs
    _VERSION = "0+unknown"


def _write_line(stream: TextIO, message: str) -> None:
    stream.write(f"{message}\n")


def _attach_bbox_arguments(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--min-lat", type=float, help="Minimum latitude.")
    parser.add_argument("--min-lon", type=float, help="Minimum longitude.")
    parser.add_argument("--max-lat", type=float, help="Maximum latitude.")
    parser.add_argument("--max-lon", type=float, help="Maximum longitude.")


def build_parser() -> argparse.ArgumentParser:
    """Build the CLI parser for the current extraction and export workflows."""

    parser = argparse.ArgumentParser(
        prog="nyc-mesh",
        description=(
            "Extract height-aware outputs from local CityGML files using the "
            "implemented nyc-mesh workflow."
        ),
        epilog=(
            "Current assumption: CityGML coordinates are in NYC EPSG:2263 and "
            "are reprojected to WGS84 (EPSG:4326) before optional clipping."
        ),
    )
    parser.add_argument(
        "--version",
        action="version",
        version=f"%(prog)s {_VERSION}",
    )

    subparsers = parser.add_subparsers(dest="command", metavar="command")
    subparsers.required = True

    for command_name, help_text, output_flag in (
        (
            "export-geojson",
            "Export the CityGML happy path to GeoJSON.",
            _run_export_geojson,
        ),
        (
            "export-geoparquet",
            "Export the CityGML happy path to GeoParquet.",
            _run_export_geoparquet,
        ),
    ):
        subparser = subparsers.add_parser(command_name, help=help_text)
        subparser.add_argument(
            "--input",
            type=Path,
            required=True,
            help="Path to a local CityGML file.",
        )
        subparser.add_argument(
            "--output",
            type=Path,
            required=True,
            help="Output path for the exported file.",
        )
        _attach_bbox_arguments(subparser)
        subparser.set_defaults(handler=output_flag, parser=subparser)

    return parser


def _build_bbox(args: argparse.Namespace) -> BoundingBox | None:
    values = (args.min_lat, args.min_lon, args.max_lat, args.max_lon)
    if all(value is None for value in values):
        return None

    if any(value is None for value in values):
        args.parser.error(
            "bbox clipping requires --min-lat, --min-lon, --max-lat, and "
            "--max-lon together"
        )

    assert args.min_lat is not None
    assert args.min_lon is not None
    assert args.max_lat is not None
    assert args.max_lon is not None
    return BoundingBox(
        min_lat=args.min_lat,
        min_lon=args.min_lon,
        max_lat=args.max_lat,
        max_lon=args.max_lon,
    )


def _run_export_geojson(args: argparse.Namespace) -> int:
    bbox = _build_bbox(args)
    buildings = extract_citygml_buildings(args.input, bbox=bbox)
    output_path = export_citygml_geojson(args.input, args.output, bbox=bbox)
    _write_line(
        sys.stdout,
        f"Exported {len(buildings)} height-aware building feature(s) to {output_path}",
    )
    return 0


def _run_export_geoparquet(args: argparse.Namespace) -> int:
    bbox = _build_bbox(args)
    buildings = extract_citygml_buildings(args.input, bbox=bbox)
    output_path = export_citygml_geoparquet(args.input, args.output, bbox=bbox)
    _write_line(
        sys.stdout,
        f"Exported {len(buildings)} height-aware building feature(s) to {output_path}",
    )
    return 0


def main(argv: Sequence[str] | None = None) -> int:
    """Run the installed ``nyc-mesh`` console script."""

    parser = build_parser()
    try:
        args = parser.parse_args(list(argv) if argv is not None else None)
        handler = cast("Callable[[argparse.Namespace], int]", args.handler)
        return handler(args)
    except SystemExit as exc:
        return exc.code if isinstance(exc.code, int) else 1
    except (
        etree.XMLSyntaxError,
        FileNotFoundError,
        OSError,
        RuntimeError,
        ValueError,
    ) as exc:
        _write_line(sys.stderr, f"nyc-mesh: error: {exc}")
        return 1
