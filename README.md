# GNSS Observations

Map Satellite ID from Android APIs to NORAD CAT IDs.

## Dataset

https://www.kaggle.com/datasets/evgenyarbatov/gnss-satellites/

## Running

Prereqs: 

- Account on https://www.space-track.org to get TLEs
- GNSSLogger app with 'Status' logging enabled
- Upload GNSSLogger logs to Google Drive


```sh
# Create venv
make venv  

# Install deps
make install  

# Replace with your own credentials
make init  

# Get GNSS IDs from https://celestrak.org
make ids  

# Filter GNSS IDs to active ones ('active' ie launched in the last 15 years)
make active  

# Download TLEs from https://www.space-track.org
make tle  

# Fetch GNSSLogger app logs from Google Drive. Replace with your own Google Drive
make log 

# Match each satellite from the logs to the closest satellite in TLE files
make match  

# Upload to Kaggle
make upload  
```

