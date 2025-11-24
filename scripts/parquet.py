import os
import json
import pandas as pd

# Directory containing the JSON files
tles_dir = "tles"

# List to hold all JSON data
data_list = []

# Loop through all files in the directory
for filename in os.listdir(tles_dir):
    if filename.endswith(".json"):
        filepath = os.path.join(tles_dir, filename)
        with open(filepath, "r") as f:
            data = json.load(f)
            data_list.append(data)

# Convert list of dicts to DataFrame
df = pd.DataFrame(data_list)

# Save to a single Parquet file
output_file = "tles/tles.parquet"
df.to_parquet(output_file, engine="pyarrow", index=False)

print(f"Saved {len(df)} TLEs to {output_file}")
