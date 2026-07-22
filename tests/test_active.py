import json
import tempfile
import unittest
from datetime import datetime
from pathlib import Path
from unittest import mock

from scripts.active import is_active, main


class IsActiveTests(unittest.TestCase):
    def test_within_cutoff_is_active(self) -> None:
        with mock.patch("scripts.active.datetime") as mock_dt:
            mock_dt.today.return_value = datetime(2026, 1, 1)
            self.assertTrue(is_active(2020))

    def test_older_than_cutoff_is_inactive(self) -> None:
        with mock.patch("scripts.active.datetime") as mock_dt:
            mock_dt.today.return_value = datetime(2026, 1, 1)
            self.assertFalse(is_active(2000))

    def test_exact_cutoff_year_is_active(self) -> None:
        with mock.patch("scripts.active.datetime") as mock_dt:
            mock_dt.today.return_value = datetime(2026, 1, 1)
            self.assertTrue(is_active(2011))


class MainTests(unittest.TestCase):
    def test_filters_active_ids_into_output_dir(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            ids_dir = Path(tmpdir) / "ids"
            active_dir = Path(tmpdir) / "active"
            ids_dir.mkdir()
            active_dir.mkdir()

            (ids_dir / "gps.json").write_text(
                json.dumps(
                    [
                        {"OBJECT_ID": "2020-001A", "NORAD_CAT_ID": 111},
                        {"OBJECT_ID": "1990-002B", "NORAD_CAT_ID": 222},
                    ]
                ),
                encoding="utf-8",
            )

            with mock.patch("scripts.active.datetime") as mock_dt:
                mock_dt.today.return_value = datetime(2026, 1, 1)
                main(str(ids_dir), str(active_dir))

            result = json.loads((active_dir / "gps.json").read_text(encoding="utf-8"))

        self.assertEqual(result, [111])


if __name__ == "__main__":
    unittest.main()
