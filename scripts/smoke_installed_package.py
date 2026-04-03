from __future__ import annotations

import importlib.resources
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

import nyc_mesh

_FIXTURE_CITYGML = """<?xml version="1.0" encoding="UTF-8"?>
<core:CityModel
  xmlns:core="http://www.opengis.net/citygml/2.0"
  xmlns:gml="http://www.opengis.net/gml"
  xmlns:bldg="http://www.opengis.net/citygml/building/2.0">
  <core:cityObjectMember>
    <bldg:Building gml:id="building-smoke">
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
</core:CityModel>
"""


def main() -> None:
    typing_marker = importlib.resources.files("nyc_mesh").joinpath("py.typed")
    if not typing_marker.is_file():
        raise SystemExit("Installed package is missing `nyc_mesh/py.typed`.")

    cli_candidates = [
        Path(sys.executable).with_name("nyc-mesh.exe"),
        Path(sys.executable).with_name("nyc-mesh"),
    ]
    fallback_cli = shutil.which("nyc-mesh")
    if fallback_cli is not None:
        cli_candidates.append(Path(fallback_cli))
    cli_path = next((candidate for candidate in cli_candidates if candidate.exists()), cli_candidates[0])
    if not cli_path.exists():
        raise SystemExit("Installed package is missing the `nyc-mesh` console script.")

    subprocess.run([str(cli_path), "--help"], check=True)

    with tempfile.TemporaryDirectory() as temp_dir:
        temp_root = Path(temp_dir)
        source_path = temp_root / "sample.gml"
        output_path = temp_root / "buildings.geojson"
        source_path.write_text(_FIXTURE_CITYGML, encoding="utf-8")
        subprocess.run(
            [
                str(cli_path),
                "export-geojson",
                "--input",
                str(source_path),
                "--output",
                str(output_path),
            ],
            check=True,
        )
        if not output_path.is_file():
            raise SystemExit(
                "Installed package could not generate the expected GeoJSON output."
            )

    version = nyc_mesh.__version__
    if not isinstance(version, str) or not version:
        raise SystemExit("Installed package did not expose a valid version string.")


if __name__ == "__main__":
    main()
