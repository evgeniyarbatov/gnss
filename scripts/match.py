import sys
import os

import pandas as pd

def main(filtered_logs_dir, matches_dir):
    log_files = [f for f in os.listdir(filtered_logs_dir) if f.endswith(".txt")]

    dfs = []
    for log_file in log_files:
        df = pd.read_csv(f"{filtered_logs_dir}/{log_file}")
        dfs.append(df)
        
    df = pd.concat(dfs, ignore_index=True)
    df = df.drop_duplicates(subset=["Svid", "ConstellationName"], keep="first")
    
    df.to_csv(f"{matches_dir}/matches.csv", index=False) 

if __name__ == "__main__":
    main(*sys.argv[1:])