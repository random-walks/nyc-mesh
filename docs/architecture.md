# Architecture

`nyc-mesh` is organized around explicit subpackages and a small set of practical
3D geodata workflows.

## Package Shape

- `nyc_mesh.models`: typed data contracts for datasets, requests, and exports
- `nyc_mesh.io`: CityGML, LiDAR, DEM, and footprint loaders
- `nyc_mesh.analysis`: extraction, clipping, joins, and terrain mesh generation
- `nyc_mesh.export`: GeoJSON, GeoParquet, glTF, and 3D Tiles outputs
- `nyc_mesh.pipeline`: higher-level convenience helpers and study-area asset
  manifests
- `nyc_mesh.cli`: installed command-line workflows

## Current data flow

1. `pipeline.build_study_area_manifest()` prepares a real local cache manifest.
2. The manifest fetches official PLUTO and building-footprint context for the
   selected bbox.
3. `io.load_citygml()` parses a local or zip-wrapped CityGML source with `lxml`.
4. `analysis.extract_buildings()` reprojects source coordinates from `EPSG:2263`
   to `EPSG:4326`.
5. `analysis.clip_to_bbox()` filters building footprints by WGS84 overlap.
6. `analysis.join_pluto()` enriches buildings from the cached official
   footprints.
7. `export.export_geojson()` / `export.export_geoparquet()` /
   `export.export_gltf()` / `export.export_3d_tiles()` produce consumer-ready
   outputs.

## Data and geography conventions

This repo now treats large public datasets as local cache assets and keeps the
consumer-facing stories under the repo-level `examples/` tree. Large public
archives stay out of git, while example reports and cache manifests stay small
and inspectable.

Shared low-level geography helpers belong in `nyc-geo-toolkit` when they are
generic and dependency-light. CityGML parsing, 3D export behavior, and
NYC-specific 3D workflow logic stay local to `nyc-mesh`.

## Planned expansion

The next layers on top of the current CityGML happy path are:

- larger-area tiling and neighborhood packaging
- bigger source-data slices
- richer browser-focused example projects
