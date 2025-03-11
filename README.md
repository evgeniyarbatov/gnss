# GNSS

Observations of GNSS satellites.

## Running

```
make venv # Create venv
make install # Install deps
make init # Relace with your own https://www.space-track.org credentials
make ids # Get GNSS IDs from https://celestrak.org
make active # Filter GNSS IDs to active ones ('active' ie launched in the last 15 years)
make tle # Download TLEs from https://www.space-track.org
make log # Fetch GNSSLogger app logs from Google Drive. Replace with your own Google Drive
make filter # Extract only the information we need from the raw logs
make match # Match each satellite from the logs to closest satellite in TLE files
make verify # Check if the match is valid
make upload # Upload to Kaggle
```

