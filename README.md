# nyc-mesh

[![Actions Status][actions-badge]][actions-link]
[![Documentation Status][rtd-badge]][rtd-link]
[![PyPI version][pypi-version]][pypi-link]
[![PyPI platforms][pypi-platforms]][pypi-link]

Python toolkit for converting NYC open CityGML buildings and LiDAR terrain into web-ready 3D geodata.

## Status

This repository is intentionally scaffolded early.

- The packaging, docs, CI, and release plumbing are in place.
- The implementation is still in the planning and seeding phase.
- There is not yet a stable public API.

## Why This Exists

NYC publishes unusually rich 3D geospatial data, but the raw assets are hard to use in practice. The source files are large, specialized, and awkward to move into browser-friendly formats. `nyc-mesh` is meant to close that gap for planners, civic hackers, researchers, journalists, and students.

The goal is to make the first useful workflow feel like:

1. Download or point at NYC source data.
2. Clip to a neighborhood or bounding box.
3. Export web-friendly outputs for mapping, rendering, or analysis.

## Planned Outputs

- GeoJSON with building heights for deck.gl and Mapbox workflows
- 3D Tiles for Cesium-style viewers
- GeoParquet for analytics pipelines
- glTF for lightweight 3D visualization

## Initial Scope

- CityGML loader for NYC building data
- Footprint and height extraction
- EPSG:2263 to EPSG:4326 reprojection
- Bounding-box clipping
- Example notebook for rendering one neighborhood in 3D

## Documentation

- `docs/project-brief.md`: who this is for and how the package should be positioned
- `docs/data-sources.md`: initial NYC datasets and provenance notes
- `docs/mvp-roadmap.md`: v0.1 scope and stretch goals
- `docs/notes/original-spec.md`: preserved seed thinking for the project

## Development

```bash
uv sync --group docs
uv run pytest
uv run mkdocs serve
```

## License

MIT.

<!-- prettier-ignore-start -->
[actions-badge]:            https://github.com/random-walks/nyc-mesh/actions/workflows/ci.yml/badge.svg
[actions-link]:             https://github.com/random-walks/nyc-mesh/actions
[github-discussions-badge]: https://img.shields.io/static/v1?label=Discussions&message=Ask&color=blue&logo=github
[github-discussions-link]:  https://github.com/random-walks/nyc-mesh/discussions
[pypi-link]:                https://pypi.org/project/nyc-mesh/
[pypi-platforms]:           https://img.shields.io/pypi/pyversions/nyc-mesh
[pypi-version]:             https://img.shields.io/pypi/v/nyc-mesh
[rtd-badge]:                https://readthedocs.org/projects/nyc-mesh/badge/?version=latest
[rtd-link]:                 https://nyc-mesh.readthedocs.io/en/latest/?badge=latest
<!-- prettier-ignore-end -->
