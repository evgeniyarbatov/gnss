import os
import time
import json
import hashlib

import pandas as pd

from functools import wraps

SIGNAL_STRENGTH_CUTOFF = 25

CACHE_DIR = "cache"
LAST_CALL_FILE = "last_omm_fetch_time.json"
ONE_HOUR = 3600


def once_per_hour_persistent(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        now = time.time()

        if os.path.exists(LAST_CALL_FILE):
            with open(LAST_CALL_FILE, "r") as f:
                try:
                    data = json.load(f)
                    last_call = data.get("last_call", 0)
                except json.JSONDecodeError:
                    last_call = 0
        else:
            last_call = 0

        if now - last_call < ONE_HOUR:
            wait_time = int(ONE_HOUR - (now - last_call))
            print(f"Function already called. Try again in {wait_time} seconds.")
            return None

        result = func(*args, **kwargs)

        with open(LAST_CALL_FILE, "w") as f:
            json.dump({"last_call": now}, f)

        return result

    return wrapper


def disk_cache(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        os.makedirs(CACHE_DIR, exist_ok=True)

        key = f"{func.__name__}:{args}:{kwargs}"
        hash_key = hashlib.sha256(key.encode()).hexdigest()
        cache_file = os.path.join(CACHE_DIR, f"{hash_key}.json")

        if os.path.exists(cache_file):
            with open(cache_file, "r") as f:
                try:
                    return json.load(f)
                except json.JSONDecodeError:
                    pass  # fallback to recomputing if cache is corrupted

        result = func(*args, **kwargs)
        with open(cache_file, "w") as f:
            json.dump(result, f)
        return result

    return wrapper


def get_name(satellite_type):
    name_map = {
        1: "navstar",
        3: "glonass",
        4: "qzs",
        5: "beidou",
        6: "galileo",
    }
    return name_map.get(satellite_type, "unknown")


def read_gnss_log(log_file):
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
        "BasebandCn0DbHz",
    ]

    df = pd.read_csv(
        log_file,
        comment="#",
        names=column_names,
        on_bad_lines="skip",
        low_memory=False,
    )

    df = df.dropna(subset=["UnixTimeMillis"])
    df[["UnixTimeMillis"]] = df[["UnixTimeMillis"]].apply(
        pd.to_numeric, errors="coerce"
    )

    # Only keep satellites for which the signal is strong enough
    df = df[df["BasebandCn0DbHz"] > SIGNAL_STRENGTH_CUTOFF]

    df["ConstellationName"] = df["ConstellationType"].apply(get_name)

    return df
