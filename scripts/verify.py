import sys
import json
import os

import pandas as pd

from zoneinfo import ZoneInfo
from datetime import datetime
from skyfield.api import EarthSatellite, load, wgs84

from scipy.spatial.distance import euclidean
from fastdtw import fastdtw

from utils import (
    read_gnss_log,
)

TIMEZONE = 'Asia/Ho_Chi_Minh'
LAT, LON = 20.99484734661426, 105.86761269335307

OBSERVATION_INTERVAL_SECONDS = 80

def filter_by_time(group):
    group = group.sort_values("datetime") 
    mask = group["datetime"].diff().dt.total_seconds().ge(OBSERVATION_INTERVAL_SECONDS)
    return group[mask | mask.isna()]

def sample_logs(df):
    df["datetime"] = pd.to_datetime(df["UnixTimeMillis"], unit="ms")
    df_filtered = df.groupby([
            "Svid", 
            "ConstellationType",
        ], 
        group_keys=False
    )[[
        "datetime",
        "UnixTimeMillis",
        "Svid", 
        "ConstellationType",
        "AzimuthDegrees",
        "ElevationDegrees",
    ]].apply(filter_by_time)
    
    return df_filtered

def predict_location(row, tles_dir):
    observer = wgs84.latlon(LAT, LON)
    
    current_time = datetime.fromtimestamp(
        row['UnixTimeMillis'] / 1000, 
        ZoneInfo(TIMEZONE),
    )
    
    omm_file_path = os.path.join(tles_dir, f"{int(row['NoradCatID'])}.json")
    with open(omm_file_path, 'r') as omm_file:
        omm_data = json.load(omm_file)[0]

    ts = load.timescale()

    satellite = EarthSatellite.from_omm(ts, omm_data)
    difference = satellite - observer

    t = ts.from_datetime(current_time)

    topocentric = difference.at(t)
    alt, az, _ = topocentric.altaz()

    return (
        az.degrees,
        alt.degrees,
    )

def main(logs_dir, tles_dir, matches_file):
    matches_df = pd.read_csv(matches_file)

    log_dfs = []
    log_files = [f for f in os.listdir(logs_dir) if f.endswith(".txt")]
    
    for log_file in log_files:
        df = read_gnss_log(f"{logs_dir}/{log_file}") 
        log_dfs.append(df)
        
    log_df = pd.concat(log_dfs, ignore_index=True)
    log_df = sample_logs(log_df)

    log_df = log_df.merge(matches_df[['Svid', 'ConstellationType', 'NoradCatID']], on=['Svid', 'ConstellationType'], how='left')
    log_df = log_df.dropna(subset=["NoradCatID"])

    log_df[['PredictedAzimuth', 'PredictedElevation']] = log_df.apply(
        lambda row: pd.Series(predict_location(
            row, 
            tles_dir=tles_dir,
        )), 
        axis=1,
    )
    
    for norad_id, group in log_df.groupby("NoradCatID"):
        measured_series = [(round(azimuth), round(elevation)) for azimuth, elevation in zip(group["AzimuthDegrees"], group["ElevationDegrees"])]
        predicted_series = [(round(azimuth), round(elevation)) for azimuth, elevation in zip(group["PredictedAzimuth"], group["PredictedElevation"])]
    
        distance, _ = fastdtw(measured_series,predicted_series, dist=euclidean)
        if distance > 0:
            print(f"Norad ID: {norad_id}, Distance: {distance}")
        
        mask = matches_df["NoradCatID"] == norad_id
        matches_df.loc[mask, ["ObservationCount"]] = len(group)
        matches_df.loc[mask, ["TLEDistance"]] = distance

    matches_df = matches_df.dropna(subset=["ObservationCount"])
    matches_df.to_csv(f"{matches_file}", index=False) 

if __name__ == "__main__":
	main(*sys.argv[1:])