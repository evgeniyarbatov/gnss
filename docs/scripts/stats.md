# stats.py

Prints coverage statistics comparing the published dataset against the full TLE catalog and theoretically visible satellites.

## Make target

```sh
make stats
```

Needs `GNSS_ENV` location variables from the Makefile.

## Usage

```sh
LAT=20.99 LON=105.87 TIMEZONE=Asia/Ho_Chi_Minh \
  python scripts/stats.py <kaggle_file> <tles_dir>
```

Example (via Make):

```sh
make stats
```

## Inputs

| Argument | Default (Makefile) | Description |
|----------|-------------------|-------------|
| `kaggle_file` | `kaggle/gnss.csv` | Published dataset |
| `tles_dir` | `tles/` | OMM JSON files |

| Environment | Source | Purpose |
|-------------|--------|---------|
| `LAT`, `LON`, `TIMEZONE` | Makefile `GNSS_ENV` | Observer position for visibility simulation |

## Outputs

Three lines printed to stdout:

```
Total: 412
Found: 102
Possible to see: 87
```

| Metric | Meaning |
|--------|---------|
| **Total** | Number of OMM files in `tles/` (active GNSS satellites tracked) |
| **Found** | Unique `(Svid, ConstellationType)` pairs in the Kaggle dataset |
| **Possible to see** | Satellites with elevation > 10° at least once over the next 24 hours from the observer location |

## Algorithm

**Possible to see** simulates visibility over a rolling 24-hour window:

1. Start at the current time in the configured `TIMEZONE`.
2. Every 30 minutes, check which satellites have elevation > 10° at `(LAT, LON)`.
3. Count the union of all visible satellites across the day.

## Dependencies

- `pandas`, `skyfield`
- [`location.py`](location.md) — observer coordinates

## Notes

- "Possible to see" is a theoretical upper bound based on current TLE data and the fixed observer location. The gap between "Possible" and "Found" reflects satellites not yet observed from this site.
- The 10° elevation threshold and 30-minute sampling interval are hardcoded in the script.
