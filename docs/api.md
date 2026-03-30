# API surface

`nyc-mesh` now has a mixed surface:

- implemented v0.1 happy-path functions
- implemented v0.1 SDK convenience helpers
- planned functions that intentionally raise `NotImplementedError`

## Implemented in v0.1

- `nyc_mesh.loaders.load_citygml`
- `nyc_mesh.processors.extract_buildings`
- `nyc_mesh.processors.clip_to_bbox`
- `nyc_mesh.exporters.export_geojson`
- `nyc_mesh.sdk.extract_citygml_buildings`
- `nyc_mesh.sdk.export_citygml_geojson`

These implement the first narrow pipeline:

1. load a local CityGML file
2. extract building footprints + measured heights
3. reproject EPSG:2263 to EPSG:4326
4. clip to a WGS84 bounding box
5. export GeoJSON

The same path is now available through the installed CLI:

```bash
nyc-mesh export-geojson \
  --input sample.gml \
  --output buildings.geojson \
  --min-lat 40.70 --min-lon -74.02 \
  --max-lat 40.72 --max-lon -73.99
```

Notes:

- `--input` must point to a local CityGML file.
- The bbox is optional, but if used all four bbox flags are required.
- The current v0.1 implementation assumes source coordinates are in `EPSG:2263`
  and reprojects them to WGS84 (`EPSG:4326`) before clipping and export.

The same path is also available through a small SDK-style surface for notebooks
and data pipelines:

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

## Still planned (explicit placeholders)

- Loaders: `load_lidar`, `load_dem`, `load_footprints`
- Processors: `join_pluto`, `generate_terrain_mesh`
- Exporters: `export_3d_tiles`, `export_geoparquet`, `export_gltf`

Planned functions are kept importable and typed so contributors can extend the
target shape without guessing.

## Models

::: nyc_mesh.models

## Loaders

::: nyc_mesh.loaders

## Processors

::: nyc_mesh.processors

## Exporters

::: nyc_mesh.exporters

## SDK

::: nyc_mesh.sdk

## CLI

::: nyc_mesh.cli
