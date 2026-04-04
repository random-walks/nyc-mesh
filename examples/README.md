# Examples

`examples/` contains self-contained consumer projects instead of notebooks.

## Contract

Every example lives in its own semantic-slug folder such as
`examples/quickstart-citygml/`.

The canonical starting point for new work is `examples/example-template/`.

Each example must:

- include its own `pyproject.toml`
- include its own `README.md`
- include its own `.gitignore`
- provide a single `main.py` entrypoint
- import only `nyc_mesh.*` as an installed package
- keep caches under `cache/`
- keep scratch and intermediate outputs under ignored `artifacts/`
- use a tracked `reports/` folder for markdown tearsheets

Examples are intentionally not part of the main CI runtime path. They are
consumer references, not package fixtures.
