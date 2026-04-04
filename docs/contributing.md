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
- prefer small, working examples over notebook-only walkthroughs
- update docs alongside package exports
- keep large raw source data out of git

## Docs and API surface

- `docs/api.md` is generated from the documented `nyc_mesh.*` public modules
- `scripts/audit_public_api.py` checks that the documented public modules and
  `__all__` exports stay aligned
- archived planning material lives under `docs/og-context/` and is intentionally
  kept out of the public docs navigation
