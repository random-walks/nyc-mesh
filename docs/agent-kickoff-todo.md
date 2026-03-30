# Agent Kickoff TODO

## Goal

Get `nyc-mesh` to a solid v0.1 foundation with:

- a clearly defined package surface
- working `NotImplementedError` placeholders wherever implementation has not landed yet
- one real happy-path implementation slice
- docs and tests that make the roadmap obvious

## Agent 1: Surface And Contracts

- Review `docs/notes/original-spec.md`, `docs/notes/gap-explination.md`, and `docs/mvp-roadmap.md`.
- Expand the package surface so every major concept in the spec has an obvious home.
- Keep unbuilt features explicit with typed placeholders and consistent `NotImplementedError` messages.
- Add module docstrings and API docs so contributors can see the target shape without reading planning notes first.

## Agent 2: Core CityGML Happy Path

- Implement the narrowest useful slice of the package:
  - load one NYC CityGML file
  - extract footprint plus measured height
  - clip to a bounding box
  - export height-aware GeoJSON
- Prefer a shallow dependency tree and readable pure-Python code where practical.
- Add tests around the first happy path rather than broad speculative infrastructure.

## Agent 3: v0.1 Docs, CLI, And Notebook Flow

- Turn the current placeholder CLI into a documented first command shape, even if only one subcommand works.
- Add or outline one notebook walkthrough for a recognizable neighborhood-scale example.
- Tighten the README so the value proposition, data sources, and first successful workflow are immediately obvious.
- Keep the rest of the planned surface scaffolded and clearly marked as future work.

## Definition Of Done For The Next Pass

- importing the package shows a coherent target surface
- the happy path is small but real
- missing features fail loudly and consistently
- docs tell a contributor exactly what exists now versus later
