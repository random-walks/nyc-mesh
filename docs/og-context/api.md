# API surface

`nyc-mesh` now has a subpackage-first public surface with a minimal root
namespace.

## Implemented in v0.1

- `nyc_mesh.io.load_citygml`
- `nyc_mesh.analysis.extract_buildings`
- `nyc_mesh.analysis.clip_to_bbox`
- `nyc_mesh.export.export_geojson`
- `nyc_mesh.pipeline.extract_citygml_buildings`
- `nyc_mesh.pipeline.export_citygml_geojson`

These implement the first narrow pipeline:

1. load a local CityGML file
2. extract building footprints + measured heights
3. reproject EPSG:2263 to EPSG:4326
4. clip to a WGS84 bounding box
5. export GeoJSON

The same path is now available through the installed CLI:

```bash
nyc-mesh export-geojson \
  --input "C:/path/to/DA_WISE_GML.zip" \
  --output buildings.geojson \
  --min-lat 40.70 --min-lon -74.02 \
  --max-lat 40.72 --max-lon -73.99
```

Notes:

- `--input` must point to a local CityGML file.
- The bbox is optional, but if used all four bbox flags are required.
- The current v0.1 implementation assumes source coordinates are in `EPSG:2263`
  and reprojects them to WGS84 (`EPSG:4326`) before clipping and export.

The same path is also available through a small pipeline surface for scripts and
data workflows:

```python
from pathlib import Path

from nyc_mesh import models, pipeline

pipeline.export_citygml_geojson(
    Path("C:/path/to/DA_WISE_GML.zip"),
    Path("buildings.geojson"),
    bbox=models.BoundingBox(
        min_lat=40.70,
        min_lon=-74.02,
        max_lat=40.72,
        max_lon=-73.99,
    ),
)
```

## Additional implemented surfaces

- Loaders: `load_lidar`, `load_dem`, `load_footprints`
- Analysis: `join_pluto`, `generate_terrain_mesh`
- Exporters: `export_3d_tiles`, `export_geoparquet`, `export_gltf`

## Models

::: nyc_mesh.models

## Loaders

::: nyc_mesh.io

## Processors

::: nyc_mesh.analysis

## Exporters

::: nyc_mesh.export

## SDK

::: nyc_mesh.pipeline

## CLI

::: nyc_mesh.cli
