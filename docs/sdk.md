# Pipeline Guide

`nyc_mesh.pipeline` provides short-path helpers on top of the lower-level
subpackage APIs.

## `extract_citygml_buildings()`

Use this helper when you want extracted height-aware building features in
memory:

```python
from pathlib import Path

from nyc_mesh import models, pipeline

features = pipeline.extract_citygml_buildings(
    Path("sample.gml"),
    bbox=models.BoundingBox(
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

from nyc_mesh import pipeline

output_path = pipeline.export_citygml_geojson(
    Path("sample.gml"),
    Path("buildings.geojson"),
)
print(output_path)
```

## `export_citygml_geoparquet()`

```python
from pathlib import Path

from nyc_mesh import pipeline

output_path = pipeline.export_citygml_geoparquet(
    Path("sample.gml"),
    Path("buildings.parquet"),
)
print(output_path)
```

## Why this layer exists

The lower-level subpackages stay readable and composable, while the pipeline
helpers give scripts and examples a short path through the current implemented
flows.
