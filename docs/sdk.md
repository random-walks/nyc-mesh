# Pipeline Guide

`nyc_mesh.pipeline` provides short-path helpers on top of the lower-level
subpackage APIs.

## `build_study_area_manifest()`

Use this helper when you want a typed cache manifest for one real study area:

```python
from pathlib import Path

from nyc_mesh import pipeline

manifest = pipeline.build_study_area_manifest(
    study_area_name="lower-manhattan-skyline",
    bbox=pipeline.DEFAULT_STUDY_AREAS["lower-manhattan-skyline"],
    cache_dir=Path("cache/lower-manhattan"),
    citygml_path=Path("C:/path/to/DA_WISE_GML.zip"),
)
print(manifest.footprints_source)
```

## `extract_citygml_buildings()`

Use this helper when you want extracted height-aware building features in
memory:

```python
from pathlib import Path

from nyc_mesh import models, pipeline

features = pipeline.extract_citygml_buildings(
    Path("C:/path/to/DA_WISE_GML.zip"),
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
    Path("C:/path/to/DA_WISE_GML.zip"),
    Path("buildings.geojson"),
)
print(output_path)
```

## `export_citygml_geoparquet()`

```python
from pathlib import Path

from nyc_mesh import pipeline

output_path = pipeline.export_citygml_geoparquet(
    Path("C:/path/to/DA_WISE_GML.zip"),
    Path("buildings.parquet"),
)
print(output_path)
```

## Why this layer exists

The lower-level subpackages stay readable and composable, while the pipeline
helpers give scripts and examples a short path through the current official-data
flows:

1. prepare a study-area manifest
2. stage or download the required archives
3. extract and clip buildings
4. export analysis-ready and browser-ready outputs
