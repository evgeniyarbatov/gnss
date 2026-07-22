import importlib
import sys
import tempfile
import unittest
from pathlib import Path

# Dynamic import: filter.py's own bare `from utils import ...` only resolves
# once scripts/ is on sys.path, and a static `from scripts.filter import ...`
# would also make mypy chase that unresolvable bare import.
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))
filter_module = importlib.import_module("filter")
filter_log = filter_module.filter_log


class FilterLogTests(unittest.TestCase):
    def test_keeps_first_observation_per_satellite(self) -> None:
        rows = [
            "Status,1690000000000,1,0,1,5,1575420030,30.0,45.0,60.0,1,1,1,30.0",
            "Status,1690000001000,1,0,1,5,1575420030,30.0,99.0,99.0,1,1,1,30.0",
            "Status,1690000002000,1,0,3,7,1575420030,30.0,10.0,20.0,1,1,1,30.0",
        ]

        with tempfile.TemporaryDirectory() as tmpdir:
            log_file = Path(tmpdir) / "gnss_log.txt"
            log_file.write_text("\n".join(rows) + "\n", encoding="utf-8")

            result_df = filter_log(str(log_file))

        self.assertEqual(len(result_df), 2)
        gps_row = result_df[result_df["Svid"] == 5].iloc[0]
        self.assertEqual(gps_row["AzimuthDegrees"], 45.0)
        self.assertEqual(gps_row["ElevationDegrees"], 60.0)
        self.assertEqual(
            list(result_df.columns),
            [
                "Svid",
                "ConstellationType",
                "ConstellationName",
                "UnixTimeMillis",
                "AzimuthDegrees",
                "ElevationDegrees",
            ],
        )


if __name__ == "__main__":
    unittest.main()
