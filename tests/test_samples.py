from __future__ import annotations

from nyc_mesh.samples import load_sample_citygml


def test_sample_citygml_loader_returns_packaged_dataset() -> None:
    dataset = load_sample_citygml()

    assert dataset.source.name == "dumbo-sample.gml"
    assert len(dataset.buildings) == 3
