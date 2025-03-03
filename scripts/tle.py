import sys
import os
import requests
import json

from ratelimit import limits, sleep_and_retry
from dotenv import load_dotenv

BASE_URL = "https://www.space-track.org/basicspacedata/query/class/gp/norad_cat_id"

# Rate limit settings: max 30 requests per 1 minute and max 300 requests per hour
MAX_CALLS_PER_MINUTE = 30
MAX_CALLS_PER_HOUR = 300

session = requests.Session()
load_dotenv("space_track.env")

def get_norad_cat_ids(active_ids_dir):
    ids = []
    for filename in os.listdir(active_ids_dir):
        if filename.endswith(".json"):
            file_path = os.path.join(active_ids_dir, filename)
            with open(file_path, 'r', encoding='utf-8') as file:
                data = json.load(file)
                if isinstance(data, list):
                    ids.extend(data)
    return ids

def authenticate():
    login_url = "https://www.space-track.org/ajaxauth/login"
    credentials = {
        "identity": os.getenv('SPACE_TRACK_USERNAME'),
        "password": os.getenv('SPACE_TRACK_PASSWORD'),
    }
    response = session.post(login_url, data=credentials)
    if response.status_code != 200:
        raise Exception("Authentication failed! Check your credentials.")

@sleep_and_retry
@limits(calls=MAX_CALLS_PER_MINUTE, period=60)
@limits(calls=MAX_CALLS_PER_HOUR, period=3600)
def fetch_omm(norad_cat_id):
    """
    Fetch the latest omm for a given NORAD CAT ID and apply rate limiting.
    """
    url = f"{BASE_URL}/{norad_cat_id}/format/json"
    response = session.get(url)
    if response.status_code == 200 and "error" not in response.text:
        return response.text.strip()
    else:
        print(f"No omm data found for NORAD CAT ID {norad_cat_id}: {response.text}")
        return None

def save_omm_to_file(filename, omm_data):
    with open(filename, "w") as file:
        omm_data = json.loads(omm_data)
        json.dump(omm_data, file, indent=4)
    print(f"Saved omm to {filename}")

def download_gnss_omm(norad_cat_ids, tles_dir):
    authenticate()
    for norad_cat_id in norad_cat_ids:
        filename = f"{norad_cat_id}.json"

        if os.path.isfile(f"{tles_dir}/{filename}"):
          continue

        omm_data = fetch_omm(norad_cat_id)
        if omm_data:
            save_omm_to_file(f"{tles_dir}/{filename}", omm_data)

def main(active_ids_dir, tles_dir):
    norad_cat_ids = get_norad_cat_ids(active_ids_dir)
    download_gnss_omm(norad_cat_ids, tles_dir)
    
    omm_files = [f for f in os.listdir(tles_dir) if f.endswith(".json")]
    assert len(omm_files) == len(norad_cat_ids), f"Expected {len(norad_cat_ids)} omm files, but found {len(omm_files)}"
    
if __name__ == "__main__":
    main(*sys.argv[1:])