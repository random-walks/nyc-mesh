# nyc-mesh

`nyc-mesh` is a Python toolkit for turning NYC open 3D source data into
web-ready geodata.

Authored by [Blaise Albis-Burdige](https://blaiseab.com/).

It focuses on the messy middle between raw public files and practical outputs
for notebooks, browsers, and spatial analysis workflows.

## What ships now

The current package provides one real CityGML happy path plus several follow-on
building blocks:

- load a local CityGML file
- extract building footprints and measured heights
- reproject from `EPSG:2263` to `EPSG:4326`
- optionally clip to a WGS84 bounding box
- export height-aware GeoJSON
- load LiDAR, DEM, and footprint data
- generate lightweight terrain meshes
- export GeoParquet, glTF, and a minimal 3D Tiles package
- run the same flow from the installed `nyc-mesh` CLI

## Positioning

This package is not a general-purpose 3D GIS platform. It is an NYC-focused tool
for getting from raw CityGML and related open data to browser-friendly or
analysis-ready outputs quickly and reproducibly.

## Docs Paths

- Hosted docs: [nyc-mesh.readthedocs.io](https://nyc-mesh.readthedocs.io/)
- Local preview: `make docs`
- Strict docs build: `make docs-build`

## Choose Your Path

- Start with [Getting Started](getting-started.md) for installation and the
  first CityGML-to-GeoJSON workflow.
- Use [CLI Reference](cli.md) for repeatable command-line usage.
- Use [SDK Guide](sdk.md) for script and pipeline-oriented helpers.
- Use [Examples](examples.md) for the repo-level reproducible walkthroughs.
- Use [Python API](api.md) for the complete public package surface.
- Use [Contributing](contributing.md) if you are maintaining or extending the
  repo.
