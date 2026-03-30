# Notebook walkthroughs

`nyc-mesh` now ships one small, reproducible notebook walkthrough for the
implemented v0.1 happy path:

- `notebooks/dumbo-citygml-geojson-walkthrough.ipynb`

## What this notebook covers

The walkthrough stays narrow and honest about current scope. It:

1. creates a small local CityGML fixture
2. uses the shipped SDK helpers to extract height-aware buildings
3. clips them to a WGS84 bounding box near DUMBO
4. exports height-aware GeoJSON
5. inspects the resulting feature payload

## Why it uses a fixture instead of a downloaded dataset

For v0.1, the notebook is designed to be reproducible in CI-like and local
environments without depending on a large external download. That keeps the
example aligned with the currently implemented package behavior:

- local CityGML files only
- measured-height buildings only
- source coordinates assumed to be `EPSG:2263`
- output reprojected to `EPSG:4326`

As the package grows, this notebook can evolve from a tiny fixture-driven
walkthrough into a neighborhood-scale example backed by a real source clip.
