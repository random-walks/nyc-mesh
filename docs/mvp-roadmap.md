# MVP Roadmap

## v0.1 Goals

- Load NYC CityGML building data for a bounded area
- Extract footprints and measured heights
- Reproject output to EPSG:4326
- Clip by bounding box
- Export height-aware GeoJSON
- Ship one notebook that renders a recognizable NYC neighborhood in 3D

## v0.1 Non-Goals

- full-city processing from day one
- production tiling for every borough
- a polished browser app
- broad support for every 3D city format

## Stretch Goals

- LiDAR-derived terrain mesh
- 3D Tiles export
- GeoParquet export
- PLUTO joins
- CLI entry points
- pre-built neighborhood clips

## Release Philosophy

The first release should be small, reproducible, and obviously useful. A narrow workflow that works cleanly is more valuable than a broad but fragile feature list.
