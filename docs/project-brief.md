# Project Brief

## Problem

NYC publishes high-value 3D geospatial data, but the raw formats are too heavy and specialized for many of the people who would benefit from them most.

## Intended Users

- urban planners
- civic hackers
- researchers
- journalists
- students

## Product Shape

`nyc-mesh` should become a reusable Python package with three main layers:

1. Load NYC source datasets from local files or URLs.
2. Transform them into clipped, web-ready geometry.
3. Export results for browsers, notebooks, and analysis pipelines.

## Why This Is Worth Building

There are building-block libraries for CityJSON, 3D Tiles, and general geospatial processing, but there is not an obvious NYC-specific package that turns raw NYC CityGML and LiDAR into easy browser-ready outputs with a lightweight Python workflow.

## Positioning

Do not position this as a general-purpose 3D GIS platform.

Position it as the fastest way to get from NYC's raw 3D open data to:

- a neighborhood mesh
- a height-aware GeoJSON
- a notebook-ready analysis artifact
- a simple web visualization input
