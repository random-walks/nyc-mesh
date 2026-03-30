# nyc-mesh

[![Actions Status][actions-badge]][actions-link]
[![Documentation Status][rtd-badge]][rtd-link]
[![PyPI version][pypi-version]][pypi-link]
[![PyPI platforms][pypi-platforms]][pypi-link]

Python toolkit for converting NYC open CityGML buildings and LiDAR terrain into
web-ready 3D geodata.

## Status

`nyc-mesh` has moved from pure scaffold to a small v0.1 foundation.

- Packaging, docs, CI, and release plumbing are in place.
- The first end-to-end happy path is implemented:
  - load one local CityGML file
  - extract footprint + measured height
  - reproject EPSG:2263 coordinates to EPSG:4326
  - clip by WGS84 bounding box
  - export height-aware GeoJSON
- A matching CLI command now ships for that same narrow workflow.
- Remaining planned features stay explicit as typed placeholders that raise
  `NotImplementedError`.

## Why This Exists

NYC publishes unusually rich 3D geospatial data, but the raw assets are hard to
use in practice. The source files are large, specialized, and awkward to move
into browser-friendly formats. `nyc-mesh` is meant to close that gap for
planners, civic hackers, researchers, journalists, and students.

The goal is to make the first useful workflow feel like:

1. Download or point at NYC source data.
2. Clip to a neighborhood or bounding box.
3. Export web-friendly outputs for mapping, rendering, or analysis.

## Implemented v0.1 Happy Path

```python
from pathlib import Path

from nyc_mesh import BoundingBox, ExportTarget
from nyc_mesh import clip_to_bbox, export_geojson, extract_buildings, load_citygml

dataset = load_citygml(Path("sample.gml"))
buildings = extract_buildings(dataset)
clipped = clip_to_bbox(
    buildings,
    BoundingBox(min_lat=40.70, min_lon=-74.02, max_lat=40.72, max_lon=-73.99),
)
export_geojson(
    clipped, ExportTarget(format="geojson", output_path=Path("buildings.geojson"))
)
```

This is intentionally narrow and designed to be reproducible before broader
format coverage lands.

## Python SDK Convenience Helpers

For notebook, ETL, and data-science-style pipelines, the same workflow is also
available through two higher-level helpers:

```python
from pathlib import Path

from nyc_mesh import BoundingBox, export_citygml_geojson, extract_citygml_buildings

bbox = BoundingBox(min_lat=40.70, min_lon=-74.02, max_lat=40.72, max_lon=-73.99)

features = extract_citygml_buildings(Path("sample.gml"), bbox=bbox)
output_path = export_citygml_geojson(
    Path("sample.gml"),
    Path("buildings.geojson"),
    bbox=bbox,
)
```

These helpers stay intentionally honest about the current v0.1 limits:

- local CityGML files only
- only buildings with `bldg:measuredHeight`
- source coordinates assumed to be `EPSG:2263`
- output reprojected to `EPSG:4326`
- optional bbox clipping in WGS84

## CLI

The installed `nyc-mesh` command now exposes the same implemented v0.1 flow:

```bash
nyc-mesh export-geojson \
  --input sample.gml \
  --output buildings.geojson \
  --min-lat 40.70 \
  --min-lon -74.02 \
  --max-lat 40.72 \
  --max-lon -73.99
```

What this command does today:

1. loads one local CityGML file
2. extracts only buildings with `bldg:measuredHeight`
3. assumes the source coordinates are NYC EPSG:2263
4. reprojects those footprints to WGS84 (EPSG:4326)
5. optionally clips them with a WGS84 bounding box
6. writes a GeoJSON `FeatureCollection`

The bounding box is optional. If you omit the four bbox flags, the command
exports every extracted height-aware building from the input file.

```bash
nyc-mesh export-geojson --input sample.gml --output buildings.geojson
```

Validation is intentionally strict and narrow:

- input must be a local file path
- bbox clipping requires all four bbox flags together
- `--min-lat < --max-lat`
- `--min-lon < --max-lon`

## Implemented Output

- GeoJSON with building heights for deck.gl and Mapbox workflows

## Planned Outputs (Not Yet Implemented)

- 3D Tiles for Cesium-style viewers
- GeoParquet for analytics pipelines
- glTF for lightweight 3D visualization

## Seeded Sources Of Truth

- `docs/notes/original-spec.md`: exact copied seed spec for `nyc-mesh`
- `docs/notes/gap-explination.md`: exact copied gap analysis that explains why
  this project is still worth building
- `docs/agent-kickoff-todo.md`: kickoff plan for follow-on implementation agents
- `docs/agent-handoff-prompt.md`: paste-ready prompt for the next agent session

## Initial Scope

- CityGML loader for NYC building data (implemented for local files)
- Footprint and height extraction (implemented)
- EPSG:2263 to EPSG:4326 reprojection (implemented)
- Bounding-box clipping (implemented)
- Example notebook for rendering one neighborhood in 3D

## Scaffolded Package Surface

The package exposes a typed surface where implemented and planned areas are both
clear:

- `nyc_mesh.loaders`
- `nyc_mesh.processors`
- `nyc_mesh.exporters`
- `nyc_mesh.models`
- `nyc_mesh.cli`

Implemented today:

- `load_citygml`
- `extract_buildings`
- `clip_to_bbox`
- `export_geojson`
- `extract_citygml_buildings`
- `export_citygml_geojson`
- `nyc-mesh export-geojson`

Still planned (`NotImplementedError`):

- `load_lidar`, `load_dem`, `load_footprints`
- `join_pluto`, `generate_terrain_mesh`
- `export_3d_tiles`, `export_geoparquet`, `export_gltf`

## Development

```bash
uv sync --group docs
uv run pytest
uv run mkdocs serve
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
