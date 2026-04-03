# nyc-mesh

`nyc-mesh` is a Python toolkit for turning NYC open 3D source data into
web-ready geodata.

It focuses on the messy middle between raw public files and practical outputs
for notebooks, browsers, and spatial analysis workflows.

## What ships now

The current `0.1` line provides one real end-to-end path:

- load a local CityGML file
- extract building footprints and measured heights
- reproject from `EPSG:2263` to `EPSG:4326`
- optionally clip to a WGS84 bounding box
- export height-aware GeoJSON
- run the same flow from the installed `nyc-mesh` CLI

## What does not ship yet

These public surfaces remain explicit placeholders:

- LiDAR and DEM loading
- terrain mesh generation
- PLUTO joins
- 3D Tiles, GeoParquet, and glTF export

## Positioning

This package is not a general-purpose 3D GIS platform. It is an NYC-focused tool
for getting from raw CityGML and related open data to browser-friendly or
analysis-ready outputs quickly and reproducibly.

## Docs Paths

- Hosted docs: [nyc-mesh.readthedocs.io](https://nyc-mesh.readthedocs.io/)
- Local preview: `make docs`
- Strict docs build: `make docs-build`
