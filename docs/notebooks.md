# Notebook Walkthroughs

`nyc-mesh` currently ships one notebook walkthrough:

- `notebooks/dumbo-citygml-geojson-walkthrough.ipynb`

## What it demonstrates

The walkthrough stays narrow and reproducible:

1. create or stage a small local CityGML sample
2. run the SDK helper path
3. clip to a DUMBO-like bounding box
4. export height-aware GeoJSON
5. inspect the resulting payload

## Why the example is small

The current package is optimized for a clean first extraction path, not a giant
download-heavy demo. The notebook mirrors that philosophy so the example remains
portable and honest about the present scope.
