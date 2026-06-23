# utils.py

Shared utilities used across the pipeline: GNSS log parsing, constellation name mapping, and API rate-limiting decorators.

Not invoked directly via Make. Imported by `filter.py`, `verify.py`, and `tle.py`.

## Functions

### `read_gnss_log(log_file)`

Parses a raw GNSSLogger `.txt` file into a pandas DataFrame.

**Parsing rules:**

- Lines starting with `#` are treated as comments and skipped.
- 14 named columns are assigned (GNSSLogger `Status` row format).
- Rows with missing `UnixTimeMillis` are dropped.
- Rows with `BasebandCn0DbHz ≤ 25` are discarded (weak signal filter).
- A `ConstellationName` column is added via `get_name()`.

**Column schema:**

| Column | Description |
|--------|-------------|
| `Status` | Row type (`Status`, `Fix`, `Raw`, etc.) |
| `UnixTimeMillis` | Observation timestamp |
| `ConstellationType` | Android constellation enum |
| `Svid` | Satellite vehicle ID |
| `AzimuthDegrees` | Reported azimuth |
| `ElevationDegrees` | Reported elevation |
| `BasebandCn0DbHz` | Signal strength |
| ... | Additional GNSSLogger fields |

### `get_name(satellite_type)`

Maps Android `ConstellationType` integers to short constellation names:

| Type | Name |
|------|------|
| 1 | `navstar` |
| 3 | `glonass` |
| 4 | `qzs` |
| 5 | `beidou` |
| 6 | `galileo` |
| other | `unknown` |

### `once_per_hour_persistent(func)`

Decorator that limits a function to one execution per hour. Persists the last call timestamp in `last_omm_fetch_time.json` at the project root. If called too soon, prints a wait message and returns `None`.

Used by `tle.py` to respect Space-Track rate limits.

### `disk_cache(func)`

Decorator that caches function return values as JSON files in `cache/`. Cache keys are SHA-256 hashes of the function name and arguments. Corrupted cache files are ignored and recomputed.

Used by `tle.py` to avoid redundant API calls.

## Constants

| Name | Value | Purpose |
|------|-------|---------|
| `SIGNAL_STRENGTH_CUTOFF` | `25` | Minimum `BasebandCn0DbHz` to keep an observation |
| `CACHE_DIR` | `cache` | Disk cache directory |
| `LAST_CALL_FILE` | `last_omm_fetch_time.json` | Rate limit timestamp file |
| `ONE_HOUR` | `3600` | Rate limit window in seconds |

## Dependencies

- `pandas`

## Notes

- Location configuration (`LAT`, `LON`, `TIMEZONE`) lives in [`location.py`](location.md), not here, so scripts that only need log parsing or caching are not required to set observer environment variables.