# Quickstart CityGML

This is the smallest end-to-end real-data `nyc-mesh` example.

It prepares a cache manifest for a named study area, fetches official PLUTO and
building-footprint context automatically, and expects a real official CityGML
archive path or an explicit opt-in download.

## Run

```bash
uv sync
uv run python main.py --citygml-path "C:/path/to/DA_WISE_GML.zip"
```

To let the example download the official CityGML archive into its cache:

```bash
uv run python main.py --allow-citygml-download
```
