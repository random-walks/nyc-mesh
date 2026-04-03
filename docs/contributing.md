# Contributing

## Development Setup

Install the default contributor environment:

```bash
make install-dev
```

Install the fuller environment, including docs and test extras:

```bash
make install
```

## Common Commands

```bash
make test
make lint
make docs
make docs-build
make ci
```

## Repository standards

- keep implemented behavior narrow, reproducible, and honest
- preserve explicit `NotImplementedError` placeholders for planned surfaces
- update docs alongside package exports
- keep large raw source data out of git

## Docs and API surface

- `docs/api.md` is generated from the top-level `nyc_mesh` namespace
- `scripts/audit_public_api.py` checks that the documented public namespace and
  `__all__` exports stay aligned
- archived planning material lives under `docs/og-context/` and is intentionally
  kept out of the public docs navigation
