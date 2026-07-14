import os
import shutil
import subprocess
import sys

import pandas as pd


def get_pretty_name(name: int) -> str:
    name_map = {
        1: "GPS",
        3: "Glonass",
        4: "QZSS",
        5: "BeiDou",
        6: "Galileo",
    }
    return name_map.get(name, "unknown")


def main(matches_file: str, kaggle_file: str) -> None:
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
    kaggle_bin = shutil.which("kaggle")
    if kaggle_bin is None:
        raise FileNotFoundError("kaggle executable not found on PATH")
    subprocess.run(  # noqa: S603 - kaggle_bin resolved via shutil.which, args are static
        [
            kaggle_bin,
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
