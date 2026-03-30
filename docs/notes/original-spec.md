# `nyc-mesh` — NYC 3D Building & Terrain Toolkit

## Resume variants: 🏛️ Civic (primary), 📊 Econ (secondary)

---

## One-liner

Python toolkit that converts NYC's open CityGML building data and LiDAR terrain
into lightweight, web-ready formats — so anyone can build 3D city visualizations
without wrestling with gigabytes of raw survey data.

---

## Why this matters to real users

NYC publishes some of the richest open 3D geodata of any city in the world:
CityGML building models, LiDAR point clouds (2010 and 2017 captures), building
footprints, and elevation models. But the raw files are enormous, in specialist
formats (GML, LAZ, TIFF), and require expensive software or deep GIS knowledge
to use.

This means that the people who _should_ be using this data — urban planners,
journalists, civic hackers, researchers, students — mostly can't. They hit a
wall at the data preparation step.

`nyc-mesh` solves the preparation problem. It's the missing pipeline between
"download from NYC Open Data" and "render in a web browser."

**Who would actually use this:**

- NYC agency staff building internal dashboards (OTI, City Planning, DEP)
- Urban studies researchers who need 3D context for spatial analysis
- Journalists doing visual stories about development, shadows, flood risk
- Anyone building on the 3D Underground (3DU) platform NYC just announced
- Students learning geospatial data processing

---

## What the end product looks like

### Core library (`nyc_mesh`)

A Python package you install with pip that provides:

1. **Loaders** — read CityGML (.gml), LiDAR (.laz), DEM (.tif), and building
   footprints (GeoJSON/Shapefile) from NYC Open Data URLs or local files
2. **Processors** — extract building geometry (footprint + height → extruded
   3D), merge with tax lot data (BBL join), clip to bounding box or neighborhood
3. **Exporters** — output to web-friendly formats:
   - GeoJSON with height attributes (for deck.gl / Mapbox)
   - 3D Tiles (for CesiumJS)
   - GeoParquet (for analytical workflows)
   - glTF (for generic 3D viewers)
4. **CLI** —
   `nyc-mesh extract --bbox "40.7,-74.01,40.72,-73.99" --format geojson` for
   quick one-liners

### Example notebook

A Jupyter notebook that:

- Downloads a neighborhood's worth of CityGML + LiDAR
- Processes it through the pipeline
- Renders a 3D visualization using deck.gl (via pydeck) or a static matplotlib
  3D plot
- Shows how to join building heights with PLUTO tax lot data for analytical use

---

## Key technical decisions

**CityGML parsing:** Use `lxml` for XML parsing rather than a heavy GIS stack.
NYC's CityGML is LoD1 (extruded footprints) which is simple geometry — no need
for a full CityGML library. Extract `gml:Polygon` coordinates and
`bldg:measuredHeight`.

**LiDAR processing:** Use `laspy` for reading LAZ/LAS files. For terrain
generation, do a simple grid interpolation (scipy) rather than requiring PDAL or
GRASS. Keep the dependency tree shallow.

**Coordinate systems:** NYC data uses EPSG:2263 (NY State Plane). Always convert
to EPSG:4326 (WGS84) for web output. Use `pyproj` for transforms. This is a
common gotcha that trips people up — handle it automatically.

**Tiling:** For large-area exports, implement simple quad-tree tiling so the
output doesn't choke web renderers. Each tile is a separate file with a manifest
JSON.

**No ESRI dependency.** The whole point is that this works with
`pip install nyc-mesh` and nothing else. No ArcPy, no QGIS, no proprietary
tools.

---

## MVP scope (weekend 1)

- [ ] CityGML loader for NYC building data (one borough at a time)
- [ ] Footprint + height extraction → GeoJSON with `height` property
- [ ] Bounding box clipping
- [ ] pydeck notebook rendering a neighborhood in 3D
- [ ] README with install, quickstart, screenshot
- [ ] Published to PyPI

## Stretch scope (weekend 2+)

- [ ] LiDAR terrain mesh generation
- [ ] 3D Tiles export for CesiumJS
- [ ] PLUTO join (BBL → tax lot attributes on each building)
- [ ] CLI tool
- [ ] GeoParquet export
- [ ] Pre-built tile sets for each community district (hosted on GitHub Releases
      or S3)

---

## README must communicate

1. **The problem:** NYC's 3D building data is incredible but inaccessible
   without specialist tools
2. **The solution:** `pip install nyc-mesh` → three lines of Python → 3D
   buildings in your browser
3. **A screenshot:** 3D rendering of a recognizable NYC neighborhood (DUMBO,
   LES, Midtown)
4. **Data sources:** Link to every NYC Open Data URL used, with license info
5. **Who it's for:** explicitly name urban planners, researchers, journalists,
   civic hackers

---

## What this proves on your resume

- You can work with CityGML, LiDAR, and the exact spatial formats NYC OTI
  manages
- You understand coordinate systems, spatial data pipelines, and web-friendly
  geo formats
- You can build developer tools (CLI, pip package) not just notebooks
- You care about making data accessible, not just analyzing it — which is the
  OTI mission
