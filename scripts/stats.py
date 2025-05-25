import sys
import os
import json

from zoneinfo import ZoneInfo
from datetime import datetime, timedelta
from skyfield.api import EarthSatellite, load, wgs84

import pandas as pd

TIMEZONE = 'Asia/Ho_Chi_Minh'
LAT, LON = 20.99484734661426, 105.86761269335307

def get_satellites_visible_now(timestamp, tles_dir):
    visible_satellites = set()
    
    observer = wgs84.latlon(LAT, LON)
    ts = load.timescale()
    t = ts.from_datetime(timestamp)

    omm_files = [
        f for f in os.listdir(tles_dir) 
        if f.endswith(".json")
    ]
    for omm_filename in omm_files:
        satellite_id = os.path.splitext(omm_filename)[0]
        omm_file_path = os.path.join(tles_dir, omm_filename)
        
        with open(omm_file_path, 'r') as omm_file:
            omm_data = json.load(omm_file)

        satellite = EarthSatellite.from_omm(ts, omm_data)
        difference = satellite - observer

        topocentric = difference.at(t)
        alt, _, _ = topocentric.altaz()

        if alt.degrees > 10:
            visible_satellites.add(satellite_id)

    return visible_satellites

def get_visible_over_day(tles_dir, interval_seconds=1800):
    start_time = datetime.now(ZoneInfo(TIMEZONE))
    end_time = start_time + timedelta(days=1)

    unique_satellites = set()

    current_time = start_time
    while current_time < end_time:
        visible_now = get_satellites_visible_now(current_time, tles_dir)
        unique_satellites.update(visible_now)
        current_time += timedelta(seconds=interval_seconds)

    return len(unique_satellites) 

def main(kaggle_file, tles_dir):
    df = pd.read_csv(kaggle_file)
    
    total_count = sum(1 for file in os.listdir(tles_dir) if file.endswith(".json"))
    print(f'Total: {total_count}')
    
    found_count = df[['Svid', 'ConstellationType']].drop_duplicates().shape[0]
    print(f'Found: {found_count}')

    possible_count = get_visible_over_day(tles_dir)
    print(f'Possible to see: {possible_count}')

if __name__ == "__main__":
	main(*sys.argv[1:])