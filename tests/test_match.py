import importlib
import os
import sys
import tempfile
import unittest
from pathlib import Path

import pandas as pd

# location.py reads LAT/LON/TIMEZONE from the environment at import time.
os.environ.setdefault("LAT", "10.0")
os.environ.setdefault("LON", "106.0")
os.environ.setdefault("TIMEZONE", "Asia/Ho_Chi_Minh")

# Dynamic import: match.py's own bare `from location import ...` only
# resolves once scripts/ is on sys.path, and a static `from scripts.match
# import ...` would also make mypy chase that unresolvable bare import.
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))
match_module = importlib.import_module("match")
get_closest_satellite = match_module.get_closest_satellite
update_matches = match_module.update_matches


class GetClosestSatelliteTests(unittest.TestCase):
    def test_returns_nearest_candidate_by_alt_az(self) -> None:
        satellite_df = pd.DataFrame(
            {
                "norad_cat_id": [111, 222, 333],
                "altitude": [10.0, 45.0, 80.0],
                "azimuth": [20.0, 50.0, 90.0],
            }
        )
        row = {"ElevationDegrees": "46.0", "AzimuthDegrees": "51.0"}

        closest = get_closest_satellite(row, satellite_df)

        self.assertEqual(closest["norad_cat_id"].iloc[0], 222)


class UpdateMatchesTests(unittest.TestCase):
    def test_merges_and_deduplicates_against_existing_file(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            existing_file = Path(tmpdir) / "matches.csv"
            pd.DataFrame({"Svid": [1], "NoradCatID": [111], "ConstellationType": [1]}).to_csv(
                existing_file, index=False
            )

            new_df = pd.DataFrame(
                {
                    "Svid": [1, 2],
                    "NoradCatID": [111, 222],
                    "ConstellationType": [1, 3],
                }
            )

            update_matches(new_df, str(existing_file))

            result = pd.read_csv(existing_file)

        self.assertEqual(len(result), 2)
        self.assertEqual(set(result["Svid"]), {1, 2})

    def test_creates_file_when_none_exists_yet(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            existing_file = Path(tmpdir) / "matches.csv"

            new_df = pd.DataFrame({"Svid": [1], "NoradCatID": [111], "ConstellationType": [1]})

            update_matches(new_df, str(existing_file))

            result = pd.read_csv(existing_file)

        self.assertEqual(len(result), 1)


if __name__ == "__main__":
    unittest.main()
