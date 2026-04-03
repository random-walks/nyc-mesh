# Getting Started

This guide shows the fastest path to the current `nyc-mesh` workflow.

## Install

```bash
pip install nyc-mesh
```

For local development:

```bash
make install-dev
```

## Export GeoJSON from CityGML

```bash
nyc-mesh export-geojson --input sample.gml --output buildings.geojson
```

You can also clip to a WGS84 bounding box:

```bash
nyc-mesh export-geojson \
  --input sample.gml \
  --output buildings.geojson \
  --min-lat 40.70 \
  --min-lon -74.02 \
  --max-lat 40.72 \
  --max-lon -73.99
```

## Use the Python API

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
- buildings must expose `bldg:measuredHeight`
- source coordinates are treated as `EPSG:2263`
- outputs are reprojected to `EPSG:4326`
