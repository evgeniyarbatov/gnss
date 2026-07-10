# match.py

Matches Android `Svid` identifiers to NORAD catalog IDs by comparing observed azimuth/elevation against TLE-predicted sky positions.

## Make target

```sh
make match
```

Requires `filter` (runs automatically as a dependency). Needs `GNSS_ENV` location variables from the Makefile.

## Usage

```sh
LAT=20.99 LON=105.87 TIMEZONE=Asia/Ho_Chi_Minh \
  python scripts/match.py <active_ids_dir> <tles_dir> <filtered_logs_dir> <matches_file>
```

Example (via Make):

```sh
make match
```

## Inputs

| Argument | Default (Makefile) | Description |
|----------|-------------------|-------------|
| `active_ids_dir` | `ids/active/` | NORAD ID lists per constellation |
| `tles_dir` | `tles/` | OMM JSON files |
| `filtered_logs_dir` | `logs/filtered/` | Filtered observation CSVs |
| `matches_file` | `logs/matched.csv` | Output lookup table |

| Environment | Source | Purpose |
|-------------|--------|---------|
| `LAT`, `LON`, `TIMEZONE` | Makefile `GNSS_ENV` | Observer position for sky prediction |

## Outputs

Appends to `logs/matched.csv`:

```
Svid,NoradCatID,ConstellationType
```

New rows are deduplicated against existing entries on `(Svid, NoradCatID, ConstellationType)`.

## Algorithm

Rows with an unmapped `ConstellationName` (`unknown`) are skipped, since there is no corresponding NORAD ID list to match against.

For each remaining unique `(Svid, ConstellationName)` across all filtered logs:

1. **Scope candidates** — load NORAD IDs for the observation's constellation from `active_ids_dir`.
2. **Predict positions** — for each candidate satellite at the observation timestamp:
   - Build a Skyfield `EarthSatellite` from the OMM file.
   - Compute topocentric azimuth and elevation from the observer (`LAT`, `LON`).
   - Keep satellites above the horizon (`altitude > 0°`).
3. **Find closest match** — build a KD-tree over `(elevation, azimuth)` of visible candidates and query with the observed position.
4. **Validate** — accept the match only if both azimuth and elevation differ by ≤ 1° from the prediction.
5. **Persist** — append accepted matches to `matched.csv`.

## Constants

| Name | Value | Purpose |
|------|-------|---------|
| `OBSERVATION_DEGREES_DELTA` | `1` | Maximum allowed deviation in azimuth and elevation |

## Dependencies

- `pandas`, `skyfield`, `scipy`
- [`location.py`](location.md) — observer coordinates

## Notes

- Matching assumes all observations were recorded near the configured `LAT`/`LON`. Wrong coordinates will produce incorrect NORAD assignments.
- Only satellites from the same constellation are considered, using Android's `ConstellationType` mapped to names like `navstar`, `glonass`, etc.