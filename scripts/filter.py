import sys
import os

import pandas as pd

def get_name(satellite_type):
    name_map = {
        1: "navstar",
        3: "glonass",
        4: "qzs",
        5: "beidou",
        6: "galileo",
    }
    return name_map.get(satellite_type, "unknown")

def filter_log(log_file):
    column_names = [
        "Status",
        "UnixTimeMillis",
        "SignalCount",
        "SignalIndex",
        "ConstellationType",
        "Svid",
        "CarrierFrequencyHz",
        "Cn0DbHz",
        "AzimuthDegrees",
        "ElevationDegrees",
        "UsedInFix",
        "HasAlmanacData",
        "HasEphemerisData",
        "BasebandCn0DbHz"
    ]

    df = pd.read_csv(
        log_file,
        comment="#",
        names=column_names,
        on_bad_lines="skip",
    )
    
    df = df.dropna(subset=["UnixTimeMillis"])
    
    df["ConstellationName"] = df["ConstellationType"].apply(get_name)
    result_df = df.drop_duplicates(subset=["Svid", "ConstellationName"], keep="first")
    
    return result_df[[
        "Svid", 
        "ConstellationName", 
        "UnixTimeMillis", 
        "AzimuthDegrees", 
        "ElevationDegrees",
    ]]

def main(logs_dir, filtered_logs_dir):
    log_files = [f for f in os.listdir(logs_dir) if f.endswith(".txt")]

    for log_file in log_files:
        result_df = filter_log(f"{logs_dir}/{log_file}")
        result_df.to_csv(f"{filtered_logs_dir}/{log_file}", index=False) 

if __name__ == "__main__":
    main(*sys.argv[1:])