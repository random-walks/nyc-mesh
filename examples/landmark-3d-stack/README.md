# Landmark 3D Stack

This example prepares a real official-data cache manifest for a famous-building
study area, clips the official CityGML archive, enriches it with real footprints
and PLUTO attributes, and optionally adds terrain outputs from a user-staged DEM
or LiDAR source.

## Run

```bash
uv sync
uv run python main.py --citygml-path "C:/path/to/DA_WISE_GML.zip"
```
