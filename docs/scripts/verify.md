# verify.py

Scores the quality of Svid-to-NORAD matches by comparing measured and TLE-predicted sky position time series using Dynamic Time Warping (DTW).

## Make target

```sh
make verify
```

Requires `match` (runs automatically as a dependency). Needs `GNSS_ENV` location variables.

## Usage

```sh
LAT=20.99 LON=105.87 TIMEZONE=Asia/Ho_Chi_Minh \
  python scripts/verify.py <logs_dir> <tles_dir> <matches_file> <verified_file>
```

Example (via Make):

```sh
make verify
```

## Inputs

| Argument | Default (Makefile) | Description |
|----------|-------------------|-------------|
| `logs_dir` | `logs/filtered/` | Log files to verify (Makefile passes filtered dir) |
| `tles_dir` | `tles/` | OMM JSON files |
| `matches_file` | `logs/matched.csv` | Matches to verify |
| `verified_file` | `logs/verified.csv` | Output scored matches |

| Environment | Source | Purpose |
|-------------|--------|---------|
| `LAT`, `LON`, `TIMEZONE` | Makefile `GNSS_ENV` | Observer position |

## Outputs

Appends to `logs/verified.csv`:

```
Svid,NoradCatID,ConstellationType,ObservationCount,TLEDistance
```

For duplicate `(Svid, NoradCatID, ConstellationType)` entries, the row with the minimum `TLEDistance` is kept.

## Algorithm

1. Load all matches from `matches_file`.
2. Read raw GNSS logs and sample observations at ≥ 80-second intervals per `(Svid, ConstellationType)`.
3. Join sampled observations with their matched NORAD ID.
4. For each NORAD ID group:
   - Predict azimuth/elevation at each timestamp using the matched satellite's OMM data.
   - Build measured and predicted time series as `(round(azimuth), round(elevation))` tuples.
   - Compute FastDTW distance between the two series.
   - Record `ObservationCount` and `TLEDistance` on the match row.
5. Keep only matches with at least one observation and write to `verified_file`.

## Constants

| Name | Value | Purpose |
|------|-------|---------|
| `OBSERVATION_INTERVAL_SECONDS` | `80` | Minimum gap between sampled observations |

## Dependencies

- `pandas`, `skyfield`, `scipy`, `fastdtw`
- [`location.py`](location.md) — observer coordinates
- [`utils.py`](utils.md) — `read_gnss_log`

## Interpreting TLEDistance

`TLEDistance` is a FastDTW score over rounded azimuth/elevation pairs. Lower values indicate better agreement between measured and predicted sky tracks. In practice, most correct matches score 0–2.

The script prints each NORAD ID with distance > 0:

```
Norad ID: 41860, Distance: 1.0
```

## Notes

- Unlike `match.py`, this script works with temporal data sampled from logs, providing a stronger validation signal than a single snapshot.
- `read_gnss_log` is designed for raw GNSSLogger `.txt` format. The Makefile currently passes `logs/filtered/`, which contains CSV files written by `filter.py`. For full time-series verification, point the script at raw logs in `logs/` instead.
