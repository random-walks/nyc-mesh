# Architecture

`nyc-mesh` is organized around a narrow but real extraction pipeline.

## Package Shape

- `nyc_mesh.loaders`: CityGML and future raw data loaders
- `nyc_mesh.processors`: extraction, reprojection, and clipping
- `nyc_mesh.exporters`: GeoJSON and future output formats
- `nyc_mesh.sdk`: higher-level convenience helpers
- `nyc_mesh.models`: typed data contracts for datasets, requests, and exports
- `nyc_mesh.cli`: installed command-line workflow

## Current data flow

1. `load_citygml()` parses a local CityGML file with `lxml`.
2. The loader extracts exterior rings and measured building heights.
3. `extract_buildings()` reprojects source coordinates from `EPSG:2263` to
   `EPSG:4326`.
4. `clip_to_bbox()` filters building footprints by WGS84 bounding-box overlap.
5. `export_geojson()` writes a browser-friendly `FeatureCollection`.

## Data and geography conventions

This repo keeps notebooks and future sample assets separate from raw source
data. Large public datasets stay out of git, while packaged fixture-style assets
and reproducible examples can live under package or notebook-friendly resource
paths as the workflow grows.

Shared low-level geography helpers belong in `nyc-geo-toolkit` when they are
generic and dependency-light. CityGML parsing, 3D export behavior, and
NYC-specific 3D workflow logic stay local to `nyc-mesh`.

## Planned expansion

The next layers on top of the current happy path are:

- LiDAR and terrain support
- richer derived exports such as 3D Tiles
- optional attribute joins
- larger-area tiling and neighborhood packaging

Those surfaces stay scaffolded until the implementation is real and testable.
