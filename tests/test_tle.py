import importlib
import json
import sys
import tempfile
import unittest
from pathlib import Path

# Dynamic import: tle.py's own bare `from utils import ...` only resolves once
# scripts/ is on sys.path, and a static `from scripts.tle import ...` would
# also make mypy chase that unresolvable bare import.
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))
tle = importlib.import_module("tle")
get_norad_cat_ids = tle.get_norad_cat_ids


class GetNoradCatIdsTests(unittest.TestCase):
    def test_aggregates_ids_across_all_json_files(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            active_dir = Path(tmpdir)
            (active_dir / "gps.json").write_text(json.dumps([1, 2]), encoding="utf-8")
            (active_dir / "glonass.json").write_text(json.dumps([3]), encoding="utf-8")
            (active_dir / "notes.txt").write_text("ignored", encoding="utf-8")

            ids = get_norad_cat_ids(str(active_dir))

        self.assertEqual(sorted(ids), [1, 2, 3])

    def test_ignores_non_list_json_contents(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            active_dir = Path(tmpdir)
            (active_dir / "bad.json").write_text(json.dumps({"not": "a list"}), encoding="utf-8")

            self.assertEqual(get_norad_cat_ids(str(active_dir)), [])


if __name__ == "__main__":
    unittest.main()
