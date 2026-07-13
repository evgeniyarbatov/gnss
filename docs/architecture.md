# Architecture

This project maps Android GNSS satellite identifiers (`Svid` + `ConstellationType`) to [NORAD catalog IDs](https://www.space-track.org) by comparing phone-reported sky positions against orbital predictions from TLE/OMM data. The result is a lookup table published as a [Kaggle dataset](https://www.kaggle.com/datasets/evgenyarbatov/gnss-satellites/).

## Problem

Android exposes opaque satellite IDs through the GNSS API. Knowing the real NORAD catalog number lets you predict which satellites are visible at a given time and place using public orbital data — useful for research, geolocation analysis, and satellite tracking.

## High-level pipeline

The pipeline has three phases: **catalog preparation**, **observation ingestion**, and **matching & publication**.

```mermaid
flowchart TD
    subgraph catalog [Catalog preparation]
        CT[CelesTrak] --> ids[ids.py]
        ids --> IDS["ids/*.json"]
        IDS --> active[active.py]
        active --> ACTIVE["ids/active/*.json"]
        ACTIVE --> tle[tle.py]
        ST[Space-Track.org] --> tle
        tle --> TLES["tles/{norad_id}.json"]
    end

    subgraph ingest [Observation ingestion]
        GD[Google Drive] --> log[log.py]
        log --> LOGS["logs/*.txt"]
        LOGS --> filter[filter.py]
        filter --> FILTERED["logs/filtered/*.txt"]
    end

    subgraph match [Matching and publication]
        FILTERED --> match[match.py]
        ACTIVE --> match
        TLES --> match
        LOC[Makefile LAT/LON/TIMEZONE] --> match
        match --> MATCHED["logs/matched.csv"]
        MATCHED --> verify[verify.py]
        FILTERED --> verify
        TLES --> verify
        verify --> VERIFIED["logs/verified.csv"]
        MATCHED --> upload[upload.py]
        upload --> KAGGLE["kaggle/gnss.csv"]
        KAGGLE --> KG[Kaggle dataset]
        KAGGLE --> stats[stats.py]
        TLES --> stats
    end
```

Run the full pipeline with:

```sh
make all
```

Or step through individual targets listed in the [Makefile](../Makefile).

## Pipeline stages

| Stage | Make target | Script | Primary output |
|-------|-------------|--------|----------------|
| Setup | `init` | — | `space_track.env`, `kaggle.env` |
| Catalog fetch | `ids` | `ids.py` | `ids/*.json` |
| Active filter | `active` | `active.py` | `ids/active/*.json` |
| TLE download | `tle` | `tle.py` | `tles/{norad_id}.json` |
| Log download | `log` | `log.py` | `logs/*.txt` |
| Log filtering | `filter` | `filter.py` | `logs/filtered/*.txt` |
| Svid matching | `match` | `match.py` | `logs/matched.csv` |
| Match verification | `verify` | `verify.py` | `logs/verified.csv` |
| Dataset upload | `upload` | `upload.py` | `kaggle/gnss.csv` + Kaggle version |
| Coverage stats | `stats` | `stats.py` | stdout summary |

Optional: `make parquet` converts all TLE JSON files into `tles/tles.parquet` for bulk analysis.

## Directory layout

```
gnss/
├── constellations.json   # GNSS constellation names for CelesTrak queries
├── ids/                  # Full NORAD catalogs per constellation (CelesTrak)
│   └── active/           # Filtered to satellites launched in last 15 years
├── tles/                 # OMM/TLE JSON files from Space-Track (one per NORAD ID)
├── logs/                 # Raw GNSSLogger .txt files from Google Drive
│   └── filtered/         # One row per satellite per log session
├── kaggle/               # Dataset files and metadata for Kaggle upload
├── cache/                # Disk cache for Space-Track API responses
├── scripts/              # Python pipeline scripts
├── Makefile              # Orchestration, paths, and observer location config
└── docs/                 # This documentation
```

## Configuration

### Observer location

Sky-position matching depends on where observations were recorded. These values are defined once in the [Makefile](../Makefile) and passed as environment variables to location-aware scripts:

| Variable | Default | Purpose |
|----------|---------|---------|
| `LAT` | `20.99484734661426` | Observer latitude (Hanoi area) |
| `LON` | `105.86761269335307` | Observer longitude |
| `TIMEZONE` | `Asia/Ho_Chi_Minh` | Timezone for timestamp conversion |

Scripts that use location import from [`location.py`](../scripts/location.py), which reads these environment variables. Change the Makefile values to match your observation site.

### Credentials

| File | Source | Used by |
|------|--------|---------|
| `space_track.env` | GitHub gist (`make init`) | `tle.py` |
| `~/.kaggle/kaggle.json` | Kaggle account settings | `upload.py` (via Kaggle CLI) |

Both files are fetched via `gh gist view` and are not committed to the repository.

### Hardcoded references

| Constant | Location | Value |
|----------|----------|-------|
| Google Drive folder ID | `log.py` | GNSSLogger log storage |
| Constellation list | `constellations.json` | qzs, beidou, glonass, navstar, galileo |
| Signal strength cutoff | `utils.py` | `BasebandCn0DbHz > 25` |
| Match tolerance | `match.py` | ±1° azimuth and elevation |
| Active satellite age | `active.py` | Launched within last 15 years |

## External data sources

- **[GNSSLogger](https://play.google.com/store/apps/details?id=com.google.android.apps.location.gps.gnsslogger)** — Android app that records raw GNSS `Status` rows to `.txt` log files.
- **[CelesTrak](https://celestrak.org)** — Public GP catalog grouped by constellation name.
- **[Space-Track.org](https://www.space-track.org)** — Authenticated OMM/TLE data for active payloads.
- **[Kaggle](https://www.kaggle.com)** — Published dataset destination.

## Core matching algorithm

The matching logic is shared across `match.py` and `verify.py`:

1. **Parse** GNSSLogger `Status` rows for `Svid`, `ConstellationType`, `AzimuthDegrees`, `ElevationDegrees`, and `UnixTimeMillis`.
2. **Filter** weak signals (`BasebandCn0DbHz ≤ 25` discarded in `read_gnss_log`).
3. **Predict** sky positions for every candidate NORAD satellite in the same constellation using [Skyfield](https://rhodesmill.org/skyfield/) and OMM data from Space-Track.
4. **Find closest** predicted position to the observed azimuth/elevation using a KD-tree (`match.py`) or time-series DTW (`verify.py`).
5. **Accept** matches where predicted and observed positions agree within tolerance.

`match.py` produces the initial `Svid → NoradCatID` mapping. `verify.py` scores each match by comparing measured and predicted sky tracks over time using [FastDTW](https://github.com/slaypni/fastdtw).

## Shared modules

| Module | Role |
|--------|------|
| [`utils.py`](../scripts/utils.py) | GNSS log parsing, constellation name mapping, API rate limiting, disk cache |
| [`location.py`](../scripts/location.py) | Observer coordinates from environment variables |

## Output artifacts

### `logs/matched.csv`

Incremental lookup table built by `match.py`:

```
Svid,NoradCatID,ConstellationType
```

### `logs/verified.csv`

Quality-scored matches from `verify.py`:

```
Svid,NoradCatID,ConstellationType,ObservationCount,TLEDistance
```

`TLEDistance` is a FastDTW score between measured and TLE-predicted azimuth/elevation time series. Lower is better; most verified matches score 0–2.

### `kaggle/gnss.csv`

Published dataset with human-readable constellation names:

```
Svid,ConstellationType,NoradCatID,ConstellationName
```

## Design notes

- **Incremental persistence**: `matched.csv` and `verified.csv` append and deduplicate across runs rather than overwriting.
- **Rate limiting**: `tle.py` wraps Space-Track fetches with a once-per-hour guard and disk cache to respect API limits.
- **Constellation scoping**: Matching only considers NORAD IDs from the same constellation as the observation, reducing the search space.
- **Single observer site**: The pipeline assumes all logs were recorded near the configured `LAT`/`LON`. Logs from other locations require updating the Makefile coordinates or extending the pipeline to use per-log positions.

## Script documentation

Each script is documented individually under [`docs/scripts/`](scripts/).
