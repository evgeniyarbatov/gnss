import json
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from scripts.ids import fetch_satellite_data, load_satellite_names, save_to_file


class LoadSatelliteNamesTests(unittest.TestCase):
    def test_loads_json_list(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            names_file = Path(tmpdir) / "constellations.json"
            names_file.write_text(json.dumps(["gps", "galileo"]), encoding="utf-8")

            self.assertEqual(load_satellite_names(str(names_file)), ["gps", "galileo"])


class SaveToFileTests(unittest.TestCase):
    def test_writes_json_to_disk(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            out_file = Path(tmpdir) / "gps.json"
            save_to_file(str(out_file), {"a": 1})

            self.assertEqual(json.loads(out_file.read_text(encoding="utf-8")), {"a": 1})


class FetchSatelliteDataTests(unittest.TestCase):
    def test_uses_group_param_for_group_query_names(self) -> None:
        response = mock.Mock(status_code=200)
        response.json.return_value = [{"NORAD_CAT_ID": 1}]

        with mock.patch("scripts.ids.requests.get", return_value=response) as mock_get:
            result = fetch_satellite_data("sbas")

        self.assertEqual(result, [{"NORAD_CAT_ID": 1}])
        called_url = mock_get.call_args.args[0]
        self.assertIn("GROUP=sbas", called_url)

    def test_uses_name_param_for_regular_names(self) -> None:
        response = mock.Mock(status_code=200)
        response.json.return_value = []

        with mock.patch("scripts.ids.requests.get", return_value=response) as mock_get:
            fetch_satellite_data("gps")

        called_url = mock_get.call_args.args[0]
        self.assertIn("NAME=gps", called_url)

    def test_returns_none_on_non_200_response(self) -> None:
        response = mock.Mock(status_code=404)

        with mock.patch("scripts.ids.requests.get", return_value=response):
            self.assertIsNone(fetch_satellite_data("gps"))


if __name__ == "__main__":
    unittest.main()
