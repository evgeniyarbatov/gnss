import sys
import os
import requests
import json

from dotenv import load_dotenv
from utils import once_per_hour_persistent, disk_cache

BASE_URL = "https://www.space-track.org/basicspacedata/query/class/gp/decay_date/null-val/epoch/>now-30/object_type/payload/norad_cat_id"

session = requests.Session()
load_dotenv("space_track.env")


def get_norad_cat_ids(active_ids_dir):
    ids = []
    for filename in os.listdir(active_ids_dir):
        if filename.endswith(".json"):
            file_path = os.path.join(active_ids_dir, filename)
            with open(file_path, "r", encoding="utf-8") as file:
                data = json.load(file)
                if isinstance(data, list):
                    ids.extend(data)
    return ids


def authenticate():
    login_url = "https://www.space-track.org/ajaxauth/login"
    credentials = {
        "identity": os.getenv("SPACE_TRACK_USERNAME"),
        "password": os.getenv("SPACE_TRACK_PASSWORD"),
    }
    response = session.post(login_url, data=credentials)
    if response.status_code != 200:
        raise Exception("Authentication failed! Check your credentials.")


@disk_cache
@once_per_hour_persistent
def fetch_omm(norad_cat_ids):
    """
    Fetch the latest omm for a given NORAD CAT ID and apply rate limiting.
    """
    url = f"{BASE_URL}/{norad_cat_ids}/format/json"
    response = session.get(url)

    if response.status_code != 200:
        raise Exception(f"Query failed: {response.status_code} {response.text}")

    return response.json()


def save_omm_to_file(filename, omm_data):
    with open(filename, "w") as file:
        json.dump(omm_data, file, indent=4)
    print(f"Saved omm to {filename}")


def download_gnss_omm(norad_cat_ids, tles_dir):
    authenticate()

    omms = fetch_omm(norad_cat_ids)
    for omm in omms:
        save_omm_to_file(f"{tles_dir}/{omm["NORAD_CAT_ID"]}.json", omm)


def main(active_ids_dir, tles_dir):
    norad_cat_ids = get_norad_cat_ids(active_ids_dir)
    download_gnss_omm(norad_cat_ids, tles_dir)

    omm_files = [f for f in os.listdir(tles_dir) if f.endswith(".json")]

    try:
        assert len(omm_files) == len(
            norad_cat_ids
        ), f"expected {len(norad_cat_ids)} omm files, but found {len(omm_files)}"
    except AssertionError as e:
        print("Some omm files are missing", e)


if __name__ == "__main__":
    main(*sys.argv[1:])
