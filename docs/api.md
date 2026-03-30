# API surface

`nyc-mesh` now has a mixed surface:

- implemented v0.1 happy-path functions
- planned functions that intentionally raise `NotImplementedError`

## Implemented in v0.1

- `nyc_mesh.loaders.load_citygml`
- `nyc_mesh.processors.extract_buildings`
- `nyc_mesh.processors.clip_to_bbox`
- `nyc_mesh.exporters.export_geojson`

These implement the first narrow pipeline:

1. load a local CityGML file
2. extract building footprints + measured heights
3. reproject EPSG:2263 to EPSG:4326
4. clip to a WGS84 bounding box
5. export GeoJSON

## Still planned (explicit placeholders)

- Loaders: `load_lidar`, `load_dem`, `load_footprints`
- Processors: `join_pluto`, `generate_terrain_mesh`
- Exporters: `export_3d_tiles`, `export_geoparquet`, `export_gltf`
- CLI execution flow

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

## CLI

::: nyc_mesh.cli
