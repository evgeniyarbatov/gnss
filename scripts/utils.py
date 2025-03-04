import pandas as pd

SIGNAL_STRENGTH_CUTOFF = 30

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
        "BasebandCn0DbHz"
    ]
    
    df = pd.read_csv(
        log_file,
        comment="#",
        names=column_names,
        on_bad_lines="skip",
    )

    df = df.dropna(subset=["UnixTimeMillis"])
    
    # Only keep satellites for which the signal is strong enough
    df = df[df['BasebandCn0DbHz'] > SIGNAL_STRENGTH_CUTOFF]
    
    df["ConstellationName"] = df["ConstellationType"].apply(get_name)
    
    return df