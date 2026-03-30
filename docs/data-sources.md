# Data Sources

## Primary Inputs

- NYC 3D building model / CityGML releases
- NYC LiDAR point cloud releases
- NYC digital elevation and terrain layers
- NYC building footprints
- NYC PLUTO tax lot data for optional attribute joins

## Initial Data Principles

- Prefer public datasets with stable URLs and documented licenses.
- Preserve provenance in exported metadata whenever practical.
- Keep the first implementation focused on one clean path through the data
  rather than supporting every possible source format at once.

## Early Technical Notes

- Expect source CRS issues and normalize to EPSG:4326 for web outputs.
- Keep large raw inputs out of git.
- Treat sample clips and notebooks as reproducible examples, not as the
  canonical data source.

## Documentation Follow-Up

As the implementation starts, this page should grow to include:

- exact dataset links
- version notes
- license notes
- expected preprocessing assumptions
