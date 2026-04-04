# Architecture

`nyc-mesh` is organized around explicit subpackages and a small set of practical
3D geodata workflows.

## Package Shape

- `nyc_mesh.models`: typed data contracts for datasets, requests, and exports
- `nyc_mesh.io`: CityGML, LiDAR, DEM, and footprint loaders
- `nyc_mesh.analysis`: extraction, clipping, joins, and terrain mesh generation
- `nyc_mesh.export`: GeoJSON, GeoParquet, glTF, and 3D Tiles outputs
- `nyc_mesh.pipeline`: higher-level convenience helpers
- `nyc_mesh.samples`: packaged sample CityGML data
- `nyc_mesh.cli`: installed command-line workflows

## Current data flow

1. `io.load_citygml()` parses a local CityGML file with `lxml`.
2. `analysis.extract_buildings()` reprojects source coordinates from `EPSG:2263`
   to `EPSG:4326`.
3. `analysis.clip_to_bbox()` filters building footprints by WGS84 overlap.
4. `export.export_geojson()` or `pipeline.export_citygml_geojson()` writes a
   browser-friendly `FeatureCollection`.
5. Optional follow-on steps include `analysis.join_pluto()`,
   `analysis.generate_terrain_mesh()`, and richer exports in `nyc_mesh.export`.

## Data and geography conventions

This repo now keeps packaged sample assets under `src/nyc_mesh/samples/data/`
and consumer-facing stories under the repo-level `examples/` tree. Large public
datasets stay out of git, while small reproducible inputs can ship with the
package or examples.

Shared low-level geography helpers belong in `nyc-geo-toolkit` when they are
generic and dependency-light. CityGML parsing, 3D export behavior, and
NYC-specific 3D workflow logic stay local to `nyc-mesh`.

## Planned expansion

The next layers on top of the current CityGML happy path are:

- larger-area tiling and neighborhood packaging
- bigger source-data slices
- richer browser-focused example projects
