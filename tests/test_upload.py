import unittest

from scripts.upload import get_pretty_name


class GetPrettyNameTests(unittest.TestCase):
    def test_known_constellation_types_are_mapped(self) -> None:
        self.assertEqual(get_pretty_name(1), "GPS")
        self.assertEqual(get_pretty_name(5), "BeiDou")

    def test_unknown_constellation_type_falls_back(self) -> None:
        self.assertEqual(get_pretty_name(99), "unknown")


if __name__ == "__main__":
    unittest.main()
