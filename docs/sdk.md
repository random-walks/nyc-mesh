# SDK Guide

The `0.1` line provides two convenience helpers on top of the loader, processor,
and exporter modules.

## `extract_citygml_buildings()`

Use this helper when you want extracted height-aware building features in
memory:

```python
from pathlib import Path

from nyc_mesh import BoundingBox, extract_citygml_buildings

features = extract_citygml_buildings(
    Path("sample.gml"),
    bbox=BoundingBox(
        min_lat=40.70,
        min_lon=-74.02,
        max_lat=40.72,
        max_lon=-73.99,
    ),
)
print(len(features))
```

## `export_citygml_geojson()`

Use this helper when you want the full happy path and a written GeoJSON file:

```python
from pathlib import Path

from nyc_mesh import export_citygml_geojson

output_path = export_citygml_geojson(
    Path("sample.gml"),
    Path("buildings.geojson"),
)
print(output_path)
```

## Why this layer exists

The lower-level modules stay readable and composable, while the SDK helpers give
notebooks and one-off scripts a short path through the current implemented flow.
