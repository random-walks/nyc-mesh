# Examples

The repo-level `examples/` tree replaces the old notebook workflow with
self-contained consumer projects.

Start with:

- `examples/quickstart-citygml/`
- `examples/landmark-3d-stack/`
- `examples/building-height-analysis/`
- `examples/example-template/`

Each example folder has its own:

- `pyproject.toml`
- `README.md`
- `.gitignore`
- `main.py`
- tracked `reports/` output
- example-local `cache/` paths for official or user-staged assets

Run any example from its own directory with:

```bash
uv sync
uv run python main.py
```
