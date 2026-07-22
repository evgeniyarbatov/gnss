import tempfile
import unittest
from pathlib import Path
from unittest import mock

from scripts.utils import disk_cache, get_name, once_per_hour_persistent, read_gnss_log


class GetNameTests(unittest.TestCase):
    def test_known_constellation_types_are_mapped(self) -> None:
        self.assertEqual(get_name(1), "navstar")
        self.assertEqual(get_name(3), "glonass")
        self.assertEqual(get_name(6), "galileo")

    def test_unknown_constellation_type_falls_back(self) -> None:
        self.assertEqual(get_name(99), "unknown")


class OncePerHourPersistentTests(unittest.TestCase):
    def test_runs_on_first_call_and_skips_within_the_hour(self) -> None:
        calls = []

        @once_per_hour_persistent
        def record() -> str:
            calls.append(1)
            return "ran"

        with tempfile.TemporaryDirectory() as tmpdir:
            last_call_file = Path(tmpdir) / "last_call.json"
            with mock.patch("scripts.utils.LAST_CALL_FILE", str(last_call_file)):
                with mock.patch("scripts.utils.time.time", return_value=10_000.0):
                    self.assertEqual(record(), "ran")

                with mock.patch("scripts.utils.time.time", return_value=10_500.0):
                    self.assertIsNone(record())

                with mock.patch("scripts.utils.time.time", return_value=10_000.0 + 3_700.0):
                    self.assertEqual(record(), "ran")

        self.assertEqual(len(calls), 2)


class DiskCacheTests(unittest.TestCase):
    def test_caches_result_on_disk_and_skips_recompute(self) -> None:
        calls = []

        @disk_cache
        def compute(x: int) -> int:
            calls.append(x)
            return x * 2

        with tempfile.TemporaryDirectory() as tmpdir:
            cache_dir = Path(tmpdir) / "cache"
            with mock.patch("scripts.utils.CACHE_DIR", str(cache_dir)):
                self.assertEqual(compute(21), 42)
                self.assertEqual(compute(21), 42)
                self.assertEqual(compute(2), 4)

        self.assertEqual(calls, [21, 2])


class ReadGnssLogTests(unittest.TestCase):
    def test_filters_non_status_rows_and_weak_signal(self) -> None:
        rows = [
            "Status,1690000000000,1,0,1,5,1575420030,30.0,45.0,60.0,1,1,1,30.0",
            "Status,1690000001000,1,0,3,7,1575420030,20.0,90.0,10.0,1,1,1,10.0",
            "Fix,1690000002000,1,0,1,9,1575420030,30.0,45.0,60.0,1,1,1,30.0",
        ]

        with tempfile.TemporaryDirectory() as tmpdir:
            log_file = Path(tmpdir) / "gnss_log.txt"
            log_file.write_text("\n".join(rows) + "\n", encoding="utf-8")

            df = read_gnss_log(str(log_file))

        self.assertEqual(list(df["Svid"]), [5])
        self.assertEqual(list(df["ConstellationName"]), ["navstar"])


if __name__ == "__main__":
    unittest.main()
