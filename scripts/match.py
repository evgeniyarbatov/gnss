import sys
import os
import json

import pandas as pd

from zoneinfo import ZoneInfo
from datetime import datetime
from skyfield.api import EarthSatellite, load, wgs84
from scipy.spatial import cKDTree

TIMEZONE = 'Asia/Ho_Chi_Minh'
LAT, LON = 20.99484734661426, 105.86761269335307

OBSERVATION_DEGREES_DELTA = 1

def get_satellite_locations(row, omm_files, tles_dir):
    observer = wgs84.latlon(LAT, LON)
    
    current_time = datetime.fromtimestamp(
        row['UnixTimeMillis'] / 1000, 
        ZoneInfo(TIMEZONE),
    )
    
    dfs = []
    for omm_filename in omm_files:
        omm_file_path = os.path.join(tles_dir, omm_filename)
        with open(omm_file_path, 'r') as omm_file:
            omm_data = json.load(omm_file)

        ts = load.timescale()

        satellite = EarthSatellite.from_omm(ts, omm_data)
        difference = satellite - observer

        t = ts.from_datetime(current_time)

        topocentric = difference.at(t)
        alt, az, _ = topocentric.altaz()

        if alt.degrees > 0:
            temp_df = pd.DataFrame({
                'norad_cat_id': [omm_data.get('NORAD_CAT_ID')],
                'altitude': [alt.degrees],
                'azimuth': [az.degrees],
            })

            dfs.append(temp_df)

    df = pd.concat(dfs, ignore_index=True)
    return df

def get_closest_satellite(row, satellite_df):
    tree = cKDTree(satellite_df[['altitude', 'azimuth']].values)
    distance, index = tree.query([[row['ElevationDegrees'], row['AzimuthDegrees']]])
    return satellite_df.iloc[index]

def get_norad_cat_id(row, active_ids_dir, tles_dir):
    with open(f"{active_ids_dir}/{row['ConstellationName']}.json", "r", encoding="utf-8") as f:
        satellite_ids = json.load(f)
    
    omm_files = [
        f for f in os.listdir(tles_dir) 
        if f.endswith(".json") and int(f.split(".")[0]) in satellite_ids
    ]

    satellite_df = get_satellite_locations(row, omm_files, tles_dir)
    closest_satellite = get_closest_satellite(row, satellite_df)
    
    return (
        closest_satellite['norad_cat_id'].iloc[0],
        closest_satellite['azimuth'].iloc[0],
        closest_satellite['altitude'].iloc[0],
    )

def update_matches(df, existing_file):
    try:
        existing_df = pd.read_csv(existing_file)
    except FileNotFoundError:
        existing_df = pd.DataFrame()

    new_data = df[['Svid', 'NoradCatID', 'ConstellationType']]

    new_data = new_data.astype(str)
    existing_df = existing_df.astype(str)

    combined_df = pd.concat([existing_df, new_data]).drop_duplicates()
    
    combined_df.to_csv(existing_file, index=False)    
    
def main(active_ids_dir, tles_dir, filtered_logs_dir, matches_file):
    log_files = [f for f in os.listdir(filtered_logs_dir) if f.endswith(".txt")]

    dfs = []
    for log_file in log_files:
        df = pd.read_csv(f"{filtered_logs_dir}/{log_file}")
        dfs.append(df)
        
    df = pd.concat(dfs, ignore_index=True)
    df = df.drop_duplicates(subset=["Svid", "ConstellationName"], keep="first")
    
    df[['NoradCatID', 'PredictedAzimuth', 'PredictedElevation']] = df.apply(
        lambda row: pd.Series(get_norad_cat_id(
            row, 
            active_ids_dir=active_ids_dir, 
            tles_dir=tles_dir,
        )), 
        axis=1,
    )
    
    df = df.rename(columns={
        "AzimuthDegrees": "ActualAzimuth", 
        "ElevationDegrees": "ActualElevation",
    })
    
    df['ElevationDelta'] = abs(df['ActualElevation'] - df['PredictedElevation'])
    df['AzimuthDelta'] = abs(df['ActualAzimuth'] - df['PredictedAzimuth'])
    
    # Allow for small deviations
    df = df[(df['ElevationDelta'] <= OBSERVATION_DEGREES_DELTA) & (df['AzimuthDelta'] <= OBSERVATION_DEGREES_DELTA)]
    
    df = df.sort_values(by='Svid')
    
    update_matches(df, matches_file)

if __name__ == "__main__":
    main(*sys.argv[1:])