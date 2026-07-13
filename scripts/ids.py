import json
import sys
import time

import requests


def load_satellite_names(filename):
    with open(filename) as file:
        return json.load(file)


GROUP_QUERY_NAMES = {"sbas"}


def fetch_satellite_data(name):
    param = "GROUP" if name in GROUP_QUERY_NAMES else "NAME"
    url = f"https://celestrak.org/NORAD/elements/gp.php?{param}={name}&FORMAT=json-pretty"
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    print(f"Failed to fetch data for {name}: {response.status_code}")
    return None


def save_to_file(filename, data):
    with open(filename, "w") as file:
        json.dump(data, file, indent=4)


def main(constellations, ids_dir):
    satellite_names = load_satellite_names(constellations)

    for name in satellite_names:
        print(f"Fetching {name}")
        data = fetch_satellite_data(name)
        if data:
            save_to_file(f"{ids_dir}/{name}.json", data)
        time.sleep(1)


if __name__ == "__main__":
    main(*sys.argv[1:])
