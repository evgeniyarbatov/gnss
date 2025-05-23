# 🛰️ GNSS Observations

Map GNSS satellite IDs from Android logs to NORAD catalog IDs
This project links GNSS satellite identifiers reported by Android devices with real-world NORAD catalog IDs using Two-Line Element sets (TLEs). It helps bridge raw GNSS observations with publicly available orbital data—useful for research, geolocation analysis, or satellite tracking.


## 📊 Dataset

Kaggle dataset:

🔗 [GNSS Satellites](https://www.kaggle.com/datasets/evgenyarbatov/gnss-satellites/)

Sources used:

- [GNSSLogger app](https://play.google.com/store/apps/details?id=com.google.android.apps.location.gps.gnsslogger&hl=en) for raw data
- [CelesTrak](https://celestrak.org) for GNSS satellite IDs
- [Space-Track.org](https://www.space-track.org/auth/login) for TLE data

## ⚙️ Getting Started

Prerequisites
- A free account on Space-Track.org
- Android device with GNSSLogger installed
  - Make sure Status logging is enabled
-  GNSS logs stored on your personal Google Drive

## 🚀 Running the Pipeline


```sh
# 1. Set up a virtual environment
make venv  

# 2. Install dependencies
make install  

# 3. Initialize project with your credentials
make init  

# 4. Download GNSS satellite IDs from CelesTrak
make ids  

# 5. Filter satellite IDs to active satellites (launched in the last 15 years)
make active  

# 6. Download current TLEs from Space-Track
make tle  

# 7. Download GNSSLogger logs from your Google Drive
make log  

# 8. Match observed GNSS satellites to closest NORAD satellites in TLEs
make match  

# 9. Upload the matched dataset to Kaggle
make upload  
```

## 📁 Project Structure

```
GNSS-Observations/
├── logs/           # GNSSLogger logs from Android devices
├── tle/            # TLE files from Space-Track
├── ids/            # Satellite IDs from CelesTrak
├── scripts/        # Matching and processing logic
├── Makefile        # Automation for all steps
└── README.md       
```
