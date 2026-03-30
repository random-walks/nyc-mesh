"""Command-line interface for the implemented v0.1 happy path."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import TYPE_CHECKING, TextIO, cast

from lxml import etree

from .models import BoundingBox
from .sdk import export_citygml_geojson, extract_citygml_buildings

if TYPE_CHECKING:
    from collections.abc import Callable, Sequence

try:
    from ._version import version as _VERSION
except ImportError:  # pragma: no cover - fallback for editable installs
    _VERSION = "0+unknown"


def _write_line(stream: TextIO, message: str) -> None:
    stream.write(f"{message}\n")


def build_parser() -> argparse.ArgumentParser:
    """Build the narrow CLI parser for the current CityGML-to-GeoJSON flow."""
    parser = argparse.ArgumentParser(
        prog="nyc-mesh",
        description=(
            "Extract height-aware GeoJSON from a local CityGML file using the "
            "implemented v0.1 workflow."
        ),
        epilog=(
            "Current v0.1 limitation: CityGML coordinates are assumed to be in "
            "NYC EPSG:2263 and are reprojected to WGS84 (EPSG:4326) before "
            "optional bbox clipping and GeoJSON export."
        ),
    )
    parser.add_argument(
        "--version",
        action="version",
        version=f"%(prog)s {_VERSION}",
    )

    subparsers = parser.add_subparsers(dest="command", metavar="command")
    subparsers.required = True

    export_geojson_parser = subparsers.add_parser(
        "export-geojson",
        help="Export the implemented CityGML happy path to GeoJSON.",
        description=(
            "Load a local CityGML file, extract buildings with measured height, "
            "optionally clip them to a WGS84 bounding box, and export GeoJSON."
        ),
        epilog=(
            "Supply all four bbox flags together to clip output. If no bbox is "
            "provided, all extracted height-aware buildings are exported."
        ),
    )
    export_geojson_parser.add_argument(
        "--input",
        type=Path,
        required=True,
        help="Path to a local CityGML file. Remote URLs are not supported in v0.1.",
    )
    export_geojson_parser.add_argument(
        "--output",
        type=Path,
        required=True,
        help="Path to the GeoJSON file to write.",
    )
    export_geojson_parser.add_argument(
        "--min-lat",
        type=float,
        help="Minimum latitude for an optional WGS84 clipping bounding box.",
    )
    export_geojson_parser.add_argument(
        "--min-lon",
        type=float,
        help="Minimum longitude for an optional WGS84 clipping bounding box.",
    )
    export_geojson_parser.add_argument(
        "--max-lat",
        type=float,
        help="Maximum latitude for an optional WGS84 clipping bounding box.",
    )
    export_geojson_parser.add_argument(
        "--max-lon",
        type=float,
        help="Maximum longitude for an optional WGS84 clipping bounding box.",
    )
    export_geojson_parser.set_defaults(
        handler=_run_export_geojson,
        parser=export_geojson_parser,
    )
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

    if args.min_lat >= args.max_lat:
        args.parser.error("--min-lat must be smaller than --max-lat")
    if args.min_lon >= args.max_lon:
        args.parser.error("--min-lon must be smaller than --max-lon")

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


def main(argv: Sequence[str] | None = None) -> int:
    """Run the installed ``nyc-mesh`` console script."""
    parser = build_parser()
    try:
        args = parser.parse_args(list(argv) if argv is not None else None)
        handler = cast("Callable[[argparse.Namespace], int]", args.handler)
        return handler(args)
    except SystemExit as exc:
        return exc.code if isinstance(exc.code, int) else 1
    except (etree.XMLSyntaxError, FileNotFoundError, OSError, ValueError) as exc:
        _write_line(sys.stderr, f"nyc-mesh: error: {exc}")
        return 1
