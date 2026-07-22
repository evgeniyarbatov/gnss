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

# Dynamic import: verify.py's own bare `from location/utils import ...` only
# resolves once scripts/ is on sys.path, and a static `from scripts.verify
# import ...` would also make mypy chase those unresolvable bare imports.
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))
verify_module = importlib.import_module("verify")
filter_by_time = verify_module.filter_by_time
sample_logs = verify_module.sample_logs
update_verified = verify_module.update_verified


class FilterByTimeTests(unittest.TestCase):
    def test_keeps_only_rows_spaced_past_the_interval(self) -> None:
        # A group's first row always has a NaT diff, which .ge() treats as False rather than NaN, so it is always dropped.
        group = pd.DataFrame(
            {
                "datetime": pd.to_datetime(
                    ["2026-01-01 00:00:00", "2026-01-01 00:00:30", "2026-01-01 00:02:00"]
                ),
                "value": [1, 2, 3],
            }
        )

        result = filter_by_time(group)

        self.assertEqual(list(result["value"]), [3])


class SampleLogsTests(unittest.TestCase):
    def test_groups_per_satellite_and_applies_time_filter(self) -> None:
        df = pd.DataFrame(
            {
                "UnixTimeMillis": [
                    1_700_000_000_000,
                    1_700_000_030_000,
                    1_700_000_200_000,
                    1_700_000_000_000,
                ],
                "Svid": [1, 1, 1, 2],
                "ConstellationType": [1, 1, 1, 1],
                "AzimuthDegrees": [10.0, 11.0, 12.0, 20.0],
                "ElevationDegrees": [30.0, 31.0, 32.0, 40.0],
            }
        )

        result = sample_logs(df)

        svid_1 = result[result["Svid"] == 1]
        self.assertEqual(len(svid_1), 1)
        self.assertEqual(svid_1["AzimuthDegrees"].iloc[0], 12.0)
        self.assertEqual(len(result[result["Svid"] == 2]), 0)


class UpdateVerifiedTests(unittest.TestCase):
    def test_keeps_minimum_tle_distance_per_satellite(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            existing_file = Path(tmpdir) / "verified.csv"
            pd.DataFrame(
                {
                    "Svid": [1],
                    "NoradCatID": [111],
                    "ConstellationType": [1],
                    "ObservationCount": [5],
                    "TLEDistance": [10.0],
                }
            ).to_csv(existing_file, index=False)

            new_df = pd.DataFrame(
                {
                    "Svid": [1],
                    "NoradCatID": [111],
                    "ConstellationType": [1],
                    "ObservationCount": [8],
                    "TLEDistance": [3.0],
                }
            )

            update_verified(new_df, str(existing_file))

            result = pd.read_csv(existing_file)

        self.assertEqual(len(result), 1)
        self.assertEqual(result["TLEDistance"].iloc[0], 3.0)


if __name__ == "__main__":
    unittest.main()
