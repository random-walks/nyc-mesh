# nyc-mesh

[![Actions Status][actions-badge]][actions-link]
[![Documentation Status][rtd-badge]][rtd-link]
[![PyPI version][pypi-version]][pypi-link]
[![PyPI platforms][pypi-platforms]][pypi-link]

Python toolkit for converting NYC open 3D source data into web-ready geodata.

Authored by [Blaise Albis-Burdige](https://blaiseab.com/).

`nyc-mesh` focuses on the messy middle between raw public CityGML releases and
practical outputs for browsers, notebooks, and reproducible analysis workflows.

## What ships in the `0.1` line

The current release implements one honest end-to-end path:

- load a local CityGML file
- extract footprint and measured height
- reproject source coordinates from `EPSG:2263` to `EPSG:4326`
- optionally clip by WGS84 bounding box
- export height-aware GeoJSON
- run the same flow from the installed `nyc-mesh` CLI

Everything else stays scaffolded with explicit `NotImplementedError`
placeholders until the implementation is real.

## Why this exists

NYC publishes unusually rich 3D geospatial data, but the raw formats are hard to
use in practice. The source files are large, specialist, and awkward to
transform into lightweight outputs for web rendering or neighborhood-scale
analysis.

This package aims to make the first useful workflow feel like:

1. point at a CityGML source file
2. extract and clip the buildings you care about
3. export a web-friendly GeoJSON artifact

## Quickstart

Install:

```bash
pip install nyc-mesh
```

Export GeoJSON from CityGML:

```bash
nyc-mesh export-geojson --input sample.gml --output buildings.geojson
```

## Python example

```python
from pathlib import Path

from nyc_mesh import BoundingBox, export_citygml_geojson

export_citygml_geojson(
    Path("sample.gml"),
    Path("buildings.geojson"),
    bbox=BoundingBox(
        min_lat=40.70,
        min_lon=-74.02,
        max_lat=40.72,
        max_lon=-73.99,
    ),
)
```

## Current assumptions

The implemented `0.1` path is intentionally narrow:

- local CityGML files only
- only buildings with `bldg:measuredHeight`
- source coordinates are treated as `EPSG:2263`
- outputs are reprojected to `EPSG:4326`
- optional clipping uses a WGS84 bounding box

## Notebook walkthrough

The repo includes a small reproducible notebook at
`notebooks/dumbo-citygml-geojson-walkthrough.ipynb` for the current happy path.

## Documentation

- Hosted docs: [nyc-mesh.readthedocs.io](https://nyc-mesh.readthedocs.io/)
- Local preview: `make docs`
- Strict docs build: `make docs-build`

## Quick links

Docs: [Home](https://nyc-mesh.readthedocs.io/en/latest/),
[Getting Started](https://nyc-mesh.readthedocs.io/en/latest/getting-started/),
[CLI Reference](https://nyc-mesh.readthedocs.io/en/latest/cli/),
[SDK Guide](https://nyc-mesh.readthedocs.io/en/latest/sdk/),
[Architecture](https://nyc-mesh.readthedocs.io/en/latest/architecture/),
[Notebooks](https://nyc-mesh.readthedocs.io/en/latest/notebooks/),
[Python API](https://nyc-mesh.readthedocs.io/en/latest/api/),
[Contributing](https://nyc-mesh.readthedocs.io/en/latest/contributing/),
[Releasing](https://nyc-mesh.readthedocs.io/en/latest/releasing/),
[Changelog](https://nyc-mesh.readthedocs.io/en/latest/changelog/)

## Development

```bash
make install-dev
make test
make lint
make docs-build
make ci
```

## License

MIT.

<!-- prettier-ignore-start -->
[actions-badge]:            https://github.com/random-walks/nyc-mesh/actions/workflows/ci.yml/badge.svg
[actions-link]:             https://github.com/random-walks/nyc-mesh/actions
[github-discussions-badge]: https://img.shields.io/static/v1?label=Discussions&message=Ask&color=blue&logo=github
[github-discussions-link]:  https://github.com/random-walks/nyc-mesh/discussions
[pypi-link]:                https://pypi.org/project/nyc-mesh/
[pypi-platforms]:           https://img.shields.io/pypi/pyversions/nyc-mesh
[pypi-version]:             https://img.shields.io/pypi/v/nyc-mesh
[rtd-badge]:                https://readthedocs.org/projects/nyc-mesh/badge/?version=latest
[rtd-link]:                 https://nyc-mesh.readthedocs.io/en/latest/?badge=latest
<!-- prettier-ignore-end -->
