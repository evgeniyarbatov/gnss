import sys
import os

import pandas as pd

from dotenv import load_dotenv
from kaggle.api.kaggle_api_extended import KaggleApi

TLE_DISTANCE_CUTOFF = 5

load_dotenv("kaggle.env")

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
			result_rows.append({
				'Svid': int(row['Svid']),
				'ConstellationType': int(row['ConstellationType']),
    			'NoradCatID': int(row['NoradCatID']),
				'ConstellationName': get_pretty_name(row['ConstellationType']),
			})
		except Exception as e:
			print(f"Error: {e}")
			continue
	
	result_df = pd.DataFrame(result_rows)
	result_df.to_csv(kaggle_file, index=False)    
    
	api = KaggleApi()
	api.authenticate()

	api.dataset_create_version(
		os.path.dirname(kaggle_file),
		'Update',
	)

if __name__ == "__main__":
	main(*sys.argv[1:])