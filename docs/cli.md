# CLI Reference

The installed `nyc-mesh` command currently exposes one implemented workflow.

## `nyc-mesh export-geojson`

```bash
nyc-mesh export-geojson --input "C:/path/to/DA_WISE_GML.zip" --output buildings.geojson
```

Clip to a WGS84 bounding box by passing all four bbox flags:

```bash
nyc-mesh export-geojson \
  --input "C:/path/to/DA_WISE_GML.zip" \
  --output buildings.geojson \
  --min-lat 40.70 \
  --min-lon -74.02 \
  --max-lat 40.72 \
  --max-lon -73.99
```

## Validation rules

- `--input` must point to a local CityGML file
- bbox clipping requires all four bbox flags together
- `--min-lat` must be smaller than `--max-lat`
- `--min-lon` must be smaller than `--max-lon`

## Output

Successful runs write a GeoJSON `FeatureCollection` containing one polygon
feature per extracted building.
