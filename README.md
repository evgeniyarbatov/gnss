# GNSS

Observations of GNSS satellites to map Satellite ID from Android APIs to NORAD CAT IDs.

## Kaggle Dataset

https://www.kaggle.com/datasets/evgenyarbatov/gnss-satellites/

## What you need

- Account on https://www.space-track.org to get TLEs
- GNSSLogger app with 'Status' logging enabled
- Upload GNSSLogger logs to Google Drive

## Running

```sh
# Create venv
make venv  

# Install deps
make install  

# Replace with your own https://www.space-track.org credentials
make init  

# Get GNSS IDs from https://celestrak.org
make ids  

# Filter GNSS IDs to active ones ('active' = launched in the last 15 years)
make active  

# Download TLEs from https://www.space-track.org
make tle  

# Fetch GNSSLogger app logs from Google Drive. Replace with your own Google Drive
make log  

# Extract only the information we need from the raw logs
make filter  

# Match each satellite from the logs to the closest satellite in TLE files
make match  

# Check if the match is valid
make verify  

# Upload to Kaggle
make upload  
```

