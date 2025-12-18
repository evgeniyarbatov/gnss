import sys
import os


from utils import (
    read_gnss_log,
)


def filter_log(log_file):
    df = read_gnss_log(log_file)

    result_df = (
        df.groupby(["Svid", "ConstellationType", "ConstellationName"])[
            ["UnixTimeMillis", "AzimuthDegrees", "ElevationDegrees"]
        ]
        .first()
        .reset_index()
    )

    return result_df[
        [
            "Svid",
            "ConstellationType",
            "ConstellationName",
            "UnixTimeMillis",
            "AzimuthDegrees",
            "ElevationDegrees",
        ]
    ]


def main(logs_dir, filtered_logs_dir):
    log_files = [f for f in os.listdir(logs_dir) if f.endswith(".txt")]

    for log_file in log_files:
        result_df = filter_log(f"{logs_dir}/{log_file}")
        result_df.to_csv(f"{filtered_logs_dir}/{log_file}", index=False)


if __name__ == "__main__":
    main(*sys.argv[1:])
