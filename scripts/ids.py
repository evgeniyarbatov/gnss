import json
import sys
import time
from typing import Any

import requests


def load_satellite_names(filename: str) -> list[str]:
    with open(filename) as file:
        return json.load(file)  # type: ignore[no-any-return]


GROUP_QUERY_NAMES = {"sbas"}


def fetch_satellite_data(name: str) -> Any | None:
    param = "GROUP" if name in GROUP_QUERY_NAMES else "NAME"
    url = f"https://celestrak.org/NORAD/elements/gp.php?{param}={name}&FORMAT=json-pretty"
    response = requests.get(url, timeout=30)
    if response.status_code == 200:
        return response.json()
    print(f"Failed to fetch data for {name}: {response.status_code}")
    return None


def save_to_file(filename: str, data: Any) -> None:
    with open(filename, "w") as file:
        json.dump(data, file, indent=4)


def main(constellations: str, ids_dir: str) -> None:
    satellite_names = load_satellite_names(constellations)

    for name in satellite_names:
        print(f"Fetching {name}")
        data = fetch_satellite_data(name)
        if data:
            save_to_file(f"{ids_dir}/{name}.json", data)
        time.sleep(1)


if __name__ == "__main__":
    main(*sys.argv[1:])
