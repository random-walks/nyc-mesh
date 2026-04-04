# Data Sources

## Primary Inputs

- NYC 3-D Building Model / CityGML archive:
  `https://maps.nyc.gov/download/3dmodel/DA_WISE_GML.zip`
- NYC Building Footprints API:
  `https://data.cityofnewyork.us/resource/5zhs-2jue.json`
- NYC PLUTO API:
  `https://data.cityofnewyork.us/resource/64uk-42ks.json`
- NYC 1-foot DEM dataset page:
  `https://data.cityofnewyork.us/City-Government/1-foot-Digital-Elevation-Model-DEM-/dpc8-z3jc/data?no_mobile=true`
- NOAA / NYC Topobathy LiDAR 2017 bulk index:
  `https://noaa-nos-coastal-lidar-pds.s3.amazonaws.com/laz/geoid18/9306/index.html`

## Initial Data Principles

- Prefer public datasets with stable URLs and documented licenses.
- Preserve provenance in exported metadata whenever practical.
- Treat CityGML, DEM, and LiDAR as local cache assets because the official
  archives are large.
- Auto-fetch the smaller supporting APIs where practical, especially PLUTO and
  building footprints.

## Early Technical Notes

- Expect source CRS issues and normalize to EPSG:4326 for web outputs.
- Keep large raw inputs out of git.
- PLUTO is easiest to fetch by bbox using centroid latitude/longitude fields.
- Building footprints are easiest to fetch by BBL after PLUTO has selected the
  study-area tax lots.
- The official building-footprint API returns `MultiPolygon` geometry and should
  not be treated as a simple `Polygon`-only source.

## Documentation Follow-Up

## Current Workflow Expectations

- CityGML can be user-staged locally or downloaded explicitly into an example or
  workflow cache.
- DEM and LiDAR are expected to be user-staged local assets for serious runs
  unless a workflow explicitly opts into a large download.
- Cache manifests should record the exact official source URLs, local asset
  paths, refresh timestamps, and row counts for smaller API-backed sources.
