import os
import sys
import json

from datetime import datetime

SATELLITE_YEAR_CUTOFF = 15

def is_active(year: int) -> bool:
    current_year = datetime.today().year
    return current_year - year <= SATELLITE_YEAR_CUTOFF

def main(ids_dir, active_ids_dir):
    ids_files = [f for f in os.listdir(ids_dir) if f.endswith(".json")]

    for ids_file in ids_files:
        active_ids = []
        
        with open(f"{ids_dir}/{ids_file}", "r", encoding="utf-8") as f:
            data = json.load(f)
        
        for satellite in data:
            object_id = satellite.get('OBJECT_ID')
            launch_year = int(object_id.split('-')[0])
            if is_active(launch_year):
                active_ids.append(satellite.get('NORAD_CAT_ID'))
                
        with open(f"{active_ids_dir}/{ids_file}", "w") as file:
            json.dump(active_ids, file, indent=4)

if __name__ == "__main__":
    main(*sys.argv[1:])