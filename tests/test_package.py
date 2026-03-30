from __future__ import annotations

import importlib.metadata
import json
from pathlib import Path

import pytest

import nyc_mesh as m
from nyc_mesh.models import (
    BoundingBox,
    CityGMLDataset,
    ExportTarget,
    NeighborhoodRequest,
)


def test_version() -> None:
    try:
        package_version = importlib.metadata.version("nyc_mesh")
    except importlib.metadata.PackageNotFoundError:
        assert m.__version__ == "0+unknown"
    else:
        assert package_version == m.__version__


def test_planned_surface_is_importable() -> None:
    bbox = BoundingBox(min_lat=40.7, min_lon=-74.01, max_lat=40.72, max_lon=-73.99)
    request = NeighborhoodRequest(name="dumbo", bbox=bbox)
    target = ExportTarget(format="geojson", output_path=Path("dummy.geojson"))

    assert request.name == "dumbo"
    assert target.format == "geojson"
    assert callable(m.load_citygml)
    assert callable(m.extract_buildings)
    assert callable(m.export_geojson)


def _write_fixture_citygml(path: Path) -> None:
    path.write_text(
        """<?xml version="1.0" encoding="UTF-8"?>
<core:CityModel
  xmlns:core="http://www.opengis.net/citygml/2.0"
  xmlns:gml="http://www.opengis.net/gml"
  xmlns:bldg="http://www.opengis.net/citygml/building/2.0">
  <core:cityObjectMember>
    <bldg:Building gml:id="building-inside">
      <bldg:measuredHeight>25.5</bldg:measuredHeight>
      <bldg:lod1Solid>
        <gml:Solid>
          <gml:exterior>
            <gml:CompositeSurface>
              <gml:surfaceMember>
                <gml:Polygon gml:id="poly-1">
                  <gml:exterior>
                    <gml:LinearRing>
                      <gml:posList srsDimension="3">
                        981000 190000 0 981100 190000 0 981100 190100 0 981000 190100 0 981000 190000 0
                      </gml:posList>
                    </gml:LinearRing>
                  </gml:exterior>
                </gml:Polygon>
              </gml:surfaceMember>
            </gml:CompositeSurface>
          </gml:exterior>
        </gml:Solid>
      </bldg:lod1Solid>
    </bldg:Building>
  </core:cityObjectMember>
  <core:cityObjectMember>
    <bldg:Building gml:id="building-outside">
      <bldg:measuredHeight>12</bldg:measuredHeight>
      <bldg:lod1Solid>
        <gml:Solid>
          <gml:exterior>
            <gml:CompositeSurface>
              <gml:surfaceMember>
                <gml:Polygon gml:id="poly-2">
                  <gml:exterior>
                    <gml:LinearRing>
                      <gml:posList srsDimension="3">
                        990000 210000 0 990100 210000 0 990100 210100 0 990000 210100 0 990000 210000 0
                      </gml:posList>
                    </gml:LinearRing>
                  </gml:exterior>
                </gml:Polygon>
              </gml:surfaceMember>
            </gml:CompositeSurface>
          </gml:exterior>
        </gml:Solid>
      </bldg:lod1Solid>
    </bldg:Building>
  </core:cityObjectMember>
  <core:cityObjectMember>
    <bldg:Building gml:id="building-no-height">
      <bldg:lod1Solid>
        <gml:Solid>
          <gml:exterior>
            <gml:CompositeSurface>
              <gml:surfaceMember>
                <gml:Polygon gml:id="poly-3">
                  <gml:exterior>
                    <gml:LinearRing>
                      <gml:posList srsDimension="3">
                        981200 190200 0 981300 190200 0 981300 190300 0 981200 190300 0 981200 190200 0
                      </gml:posList>
                    </gml:LinearRing>
                  </gml:exterior>
                </gml:Polygon>
              </gml:surfaceMember>
            </gml:CompositeSurface>
          </gml:exterior>
        </gml:Solid>
      </bldg:lod1Solid>
    </bldg:Building>
  </core:cityObjectMember>
</core:CityModel>
""",
        encoding="utf-8",
    )


def test_citygml_happy_path_to_geojson(tmp_path: Path) -> None:
    source_path = tmp_path / "sample.gml"
    _write_fixture_citygml(source_path)

    loaded = m.load_citygml(source_path)
    assert isinstance(loaded, CityGMLDataset)
    assert len(loaded.buildings) == 3

    extracted = m.extract_buildings(loaded)
    # Building without measuredHeight is dropped in v0.1.
    assert {feature.building_id for feature in extracted} == {
        "building-inside",
        "building-outside",
    }

    clipped = m.clip_to_bbox(
        extracted,
        BoundingBox(
            min_lat=40.687,
            min_lon=-74.03,
            max_lat=40.705,
            max_lon=-74.0,
        ),
    )
    assert [feature.building_id for feature in clipped] == ["building-inside"]

    output_path = m.export_geojson(
        clipped,
        ExportTarget(format="geojson", output_path=tmp_path / "buildings.geojson"),
    )
    payload = json.loads(output_path.read_text(encoding="utf-8"))
    assert payload["type"] == "FeatureCollection"
    assert len(payload["features"]) == 1
    first = payload["features"][0]
    assert first["id"] == "building-inside"
    assert first["properties"]["height"] == 25.5
    assert first["geometry"]["type"] == "Polygon"
    assert len(first["geometry"]["coordinates"][0]) >= 4


def test_cli_export_geojson_with_bbox(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    source_path = tmp_path / "sample.gml"
    output_path = tmp_path / "buildings.geojson"
    _write_fixture_citygml(source_path)

    exit_code = m.main(
        [
            "export-geojson",
            "--input",
            str(source_path),
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
    assert str(output_path.resolve()) in captured.out
    assert captured.err == ""

    payload = json.loads(output_path.read_text(encoding="utf-8"))
    assert [feature["id"] for feature in payload["features"]] == ["building-inside"]


def test_cli_export_geojson_without_bbox_exports_all_height_aware_buildings(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    source_path = tmp_path / "sample.gml"
    output_path = tmp_path / "all-buildings.geojson"
    _write_fixture_citygml(source_path)

    exit_code = m.main(
        [
            "export-geojson",
            "--input",
            str(source_path),
            "--output",
            str(output_path),
        ]
    )

    captured = capsys.readouterr()
    assert exit_code == 0
    assert "Exported 2 height-aware building feature(s)" in captured.out
    assert captured.err == ""

    payload = json.loads(output_path.read_text(encoding="utf-8"))
    assert [feature["id"] for feature in payload["features"]] == [
        "building-inside",
        "building-outside",
    ]


def test_cli_requires_complete_bbox(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    source_path = tmp_path / "sample.gml"
    output_path = tmp_path / "buildings.geojson"
    _write_fixture_citygml(source_path)

    exit_code = m.main(
        [
            "export-geojson",
            "--input",
            str(source_path),
            "--output",
            str(output_path),
            "--min-lat",
            "40.687",
        ]
    )

    captured = capsys.readouterr()
    assert exit_code == 2
    assert captured.out == ""
    assert (
        "bbox clipping requires --min-lat, --min-lon, --max-lat, and --max-lon together"
        in captured.err
    )


def test_cli_rejects_inverted_bbox(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    source_path = tmp_path / "sample.gml"
    output_path = tmp_path / "buildings.geojson"
    _write_fixture_citygml(source_path)

    exit_code = m.main(
        [
            "export-geojson",
            "--input",
            str(source_path),
            "--output",
            str(output_path),
            "--min-lat",
            "40.705",
            "--min-lon",
            "-74.03",
            "--max-lat",
            "40.687",
            "--max-lon",
            "-74.0",
        ]
    )

    captured = capsys.readouterr()
    assert exit_code == 2
    assert captured.out == ""
    assert "--min-lat must be smaller than --max-lat" in captured.err


def test_cli_reports_missing_input_file(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    output_path = tmp_path / "buildings.geojson"

    exit_code = m.main(
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
    assert captured.out == ""
    assert "nyc-mesh: error: CityGML source does not exist:" in captured.err


def test_cli_reports_invalid_xml(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    source_path = tmp_path / "broken.gml"
    output_path = tmp_path / "buildings.geojson"
    source_path.write_text("<broken>", encoding="utf-8")

    exit_code = m.main(
        [
            "export-geojson",
            "--input",
            str(source_path),
            "--output",
            str(output_path),
        ]
    )

    captured = capsys.readouterr()
    assert exit_code == 1
    assert captured.out == ""
    assert "nyc-mesh: error:" in captured.err


def test_cli_help_mentions_current_crs_assumption(
    capsys: pytest.CaptureFixture[str],
) -> None:
    exit_code = m.main(["--help"])

    captured = capsys.readouterr()
    assert exit_code == 0
    assert "export-geojson" in captured.out
    assert "EPSG:2263" in captured.out
    assert captured.err == ""


def test_load_citygml_rejects_http_sources() -> None:
    with pytest.raises(ValueError, match="local file paths only"):
        m.load_citygml("https://example.com/buildings.gml")


def test_unimplemented_surfaces_raise_consistently() -> None:
    with pytest.raises(NotImplementedError, match="planned nyc-mesh surface"):
        m.load_lidar(Path("sample.laz"))
    with pytest.raises(NotImplementedError, match="planned nyc-mesh surface"):
        m.join_pluto((), object())
    with pytest.raises(NotImplementedError, match="planned nyc-mesh surface"):
        m.export_3d_tiles((), ExportTarget("3dtiles", Path("x")))
