import sys
import os
import json

import pandas as pd

from zoneinfo import ZoneInfo
from datetime import datetime, timedelta
from skyfield.api import EarthSatellite, load, wgs84

LAT, LON = 20.99484734661426, 105.86761269335307

def get_norad_cat_id(row, active_ids_dir, tles_dir):
    with open(f"{active_ids_dir}/{row['ConstellationName']}.json", "r", encoding="utf-8") as f:
        satellite_ids = json.load(f)
    
    omm_files = [f for f in os.listdir(tles_dir) if f.endswith(".json") and int(f.split(".")[0]) in satellite_ids]
    print(row['ConstellationName'], omm_files)

def main(active_ids_dir, tles_dir, filtered_logs_dir, matches_dir):
    log_files = [f for f in os.listdir(filtered_logs_dir) if f.endswith(".txt")]

    dfs = []
    for log_file in log_files:
        df = pd.read_csv(f"{filtered_logs_dir}/{log_file}")
        dfs.append(df)
        
    df = pd.concat(dfs, ignore_index=True)
    df = df.drop_duplicates(subset=["Svid", "ConstellationName"], keep="first")
    
    df['NoradCatID'] = df.apply(
        lambda row: get_norad_cat_id(
            row, 
            active_ids_dir=active_ids_dir, 
            tles_dir=tles_dir,
        ), 
        axis=1,
    )
    
    df.to_csv(f"{matches_dir}/matches.csv", index=False) 

if __name__ == "__main__":
    main(*sys.argv[1:])