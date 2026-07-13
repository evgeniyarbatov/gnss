# Documentation

Technical documentation for the GNSS Observations pipeline.

## Overview

- [Architecture](architecture.md) — pipeline design, data flow, configuration, and output artifacts

## Scripts

| Script | Make target | Description |
|--------|-------------|-------------|
| [ids.py](scripts/ids.md) | `make ids` | Fetch NORAD catalogs from CelesTrak |
| [active.py](scripts/active.md) | `make active` | Filter to recently launched satellites |
| [tle.py](scripts/tle.md) | `make tle` | Download OMM/TLE data from Space-Track |
| [log.py](scripts/log.md) | `make log` | Download GNSSLogger logs from Google Drive |
| [filter.py](scripts/filter.md) | `make filter` | Collapse logs to one row per satellite |
| [match.py](scripts/match.md) | `make match` | Match Svid to NORAD ID via sky position |
| [verify.py](scripts/verify.md) | `make verify` | Score matches with time-series DTW |
| [upload.py](scripts/upload.md) | `make upload` | Publish dataset to Kaggle |
| [stats.py](scripts/stats.md) | `make stats` | Print coverage statistics |
| [parquet.py](scripts/parquet.md) | `make parquet` | Convert TLE JSON to Parquet |
| [utils.py](scripts/utils.md) | — | Shared helpers and log parsing |
| [location.py](scripts/location.md) | — | Observer coordinates from env vars |
