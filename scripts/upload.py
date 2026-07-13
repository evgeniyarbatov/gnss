import os
import subprocess
import sys

import pandas as pd


def get_pretty_name(name):
    name_map = {
        1: "GPS",
        3: "Glonass",
        4: "QZSS",
        5: "BeiDou",
        6: "Galileo",
    }
    return name_map.get(name, "unknown")


def main(matches_file, kaggle_file):
    df = pd.read_csv(matches_file)

    result_rows = []
    for _, row in df.iterrows():
        try:
            result_rows.append(
                {
                    "Svid": int(row["Svid"]),
                    "ConstellationType": int(row["ConstellationType"]),
                    "NoradCatID": int(row["NoradCatID"]),
                    "ConstellationName": get_pretty_name(row["ConstellationType"]),
                }
            )
        except Exception as e:
            print(f"Error: {e}")
            continue

    result_df = pd.DataFrame(result_rows)
    result_df.to_csv(kaggle_file, index=False)

    dataset_dir = os.path.dirname(kaggle_file)
    subprocess.run(
        [
            "kaggle",
            "datasets",
            "version",
            "-p",
            dataset_dir,
            "-m",
            "Update",
        ],
        check=True,
    )


if __name__ == "__main__":
    main(*sys.argv[1:])
