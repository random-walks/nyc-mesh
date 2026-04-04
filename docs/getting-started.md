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

from nyc_mesh import models, pipeline

pipeline.export_citygml_geojson(
    Path("sample.gml"),
    Path("buildings.geojson"),
    bbox=models.BoundingBox(
        min_lat=40.70,
        min_lon=-74.02,
        max_lat=40.72,
        max_lon=-73.99,
    ),
)
```

## More than GeoJSON

The same extracted buildings can also feed:

- `nyc_mesh.export.export_geoparquet()` for analysis workflows
- `nyc_mesh.export.export_gltf()` for lightweight 3D viewers
- `nyc_mesh.export.export_3d_tiles()` for a minimal Cesium package

## Current assumptions

The CityGML happy path is intentionally opinionated:

- local CityGML files only
- buildings must expose `bldg:measuredHeight`
- source coordinates are treated as `EPSG:2263`
- outputs are reprojected to `EPSG:4326`
