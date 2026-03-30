# nyc-mesh

`nyc-mesh` is a Python-first toolkit for turning NYC open 3D source data into
outputs that are practical for web visualization and spatial analysis.

The project started from a clean package scaffold so the repository can grow in
public with stable packaging, CI, documentation, and release hygiene from the
beginning.

The current v0.1 state now includes one real happy path:

- load local CityGML
- extract footprints + measured heights
- reproject EPSG:2263 to EPSG:4326
- clip by WGS84 bounding box
- export height-aware GeoJSON

Everything else remains scaffolded with explicit `NotImplementedError`
placeholders.

This docs site now includes two exact source documents imported from the
showcase planning repo:

- the original `nyc-mesh` seed spec
- the gap explanation for why this is still a real OSS opportunity

## Project Focus

- Keep the dependency stack lightweight for a geospatial workflow
- Handle NYC-specific gotchas like EPSG:2263 reprojection automatically
- Make small-area extraction easy before tackling large-area tiling
- Produce outputs that fit both browser rendering and analytical workflows

## Read Next

- [Project brief](project-brief.md)
- [Data sources](data-sources.md)
- [MVP roadmap](mvp-roadmap.md)
- [Agent kickoff TODO](agent-kickoff-todo.md)
- [Agent handoff prompt](agent-handoff-prompt.md)
- [Original seed spec](notes/original-spec.md)
- [Gap explination](notes/gap-explination.md)
