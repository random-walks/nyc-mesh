from __future__ import annotations

from pathlib import Path

import pytest

from nyc_mesh.cli import main
from tests.helpers import sample_citygml_path


def test_cli_export_geojson_with_bbox(
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    output_path = tmp_path / "buildings.geojson"
    exit_code = main(
        [
            "export-geojson",
            "--input",
            str(sample_citygml_path()),
            "--output",
            str(output_path),
            "--min-lat",
            "40.687",
            "--min-lon",
            "-74.03",
            "--max-lat",
            "40.705",
            "--max-lon",
            "-74.0",
        ]
    )
    captured = capsys.readouterr()

    assert exit_code == 0
    assert "Exported 1 height-aware building feature(s)" in captured.out
    assert output_path.exists()


def test_cli_export_geoparquet(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    output_path = tmp_path / "buildings.parquet"
    exit_code = main(
        [
            "export-geoparquet",
            "--input",
            str(sample_citygml_path()),
            "--output",
            str(output_path),
        ]
    )
    captured = capsys.readouterr()

    assert exit_code == 0
    assert "Exported 2 height-aware building feature(s)" in captured.out
    assert output_path.exists()


def test_cli_requires_complete_bbox(
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    output_path = tmp_path / "buildings.geojson"
    exit_code = main(
        [
            "export-geojson",
            "--input",
            str(sample_citygml_path()),
            "--output",
            str(output_path),
            "--min-lat",
            "40.687",
        ]
    )
    captured = capsys.readouterr()

    assert exit_code == 2
    assert "bbox clipping requires" in captured.err


def test_cli_reports_missing_input_file(
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    output_path = tmp_path / "buildings.geojson"
    exit_code = main(
        [
            "export-geojson",
            "--input",
            str(tmp_path / "missing.gml"),
            "--output",
            str(output_path),
        ]
    )
    captured = capsys.readouterr()

    assert exit_code == 1
    assert "CityGML source does not exist" in captured.err
