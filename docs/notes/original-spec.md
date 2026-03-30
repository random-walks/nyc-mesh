# Original Spec Notes

## One-Liner

Python toolkit that converts NYC open CityGML building data and LiDAR terrain into lightweight, web-ready formats so developers and analysts can build 3D city visualizations without wrestling with raw survey files.

## Core Idea

The package should sit between "download from NYC Open Data" and "render in a browser."

## Expected Library Surface

- loaders for CityGML, LAZ, TIFF, and footprint sources
- processors for geometry extraction, clipping, and joins
- exporters for GeoJSON, 3D Tiles, GeoParquet, and glTF
- a CLI for quick extraction workflows

## Key Technical Choices

- use `lxml` for CityGML parsing
- use `laspy` for LiDAR access
- use `pyproj` for CRS transforms
- avoid proprietary GIS dependencies
- prefer lightweight tiling and export logic over heavy infrastructure

## Intended Showcase Value

This project is meant to demonstrate:

- practical work with NYC geospatial formats
- understanding of CRS and spatial pipelines
- developer-tool thinking, not just notebook analysis
- public, reusable proof of work
