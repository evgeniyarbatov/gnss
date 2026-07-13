# tle.py

Downloads Orbit Mean Elements Message (OMM) data from [Space-Track.org](https://www.space-track.org) for every active NORAD catalog ID.

## Make target

```sh
make tle
```

Requires `space_track.env` credentials (from `make init`) and populated `ids/active/`.

## Usage

```sh
python scripts/tle.py <active_ids_dir> <tles_dir>
```

Example:

```sh
python scripts/tle.py ids/active/ tles/
```

## Inputs

| Argument | Default (Makefile) | Description |
|----------|-------------------|-------------|
| `active_ids_dir` | `ids/active/` | NORAD ID lists per constellation |
| `tles_dir` | `tles/` | Output directory for OMM JSON files |

| Credential file | Variables |
|-----------------|-----------|
| `space_track.env` | `SPACE_TRACK_USERNAME`, `SPACE_TRACK_PASSWORD` |

## Outputs

One JSON file per satellite:

```
tles/62339.json
tles/41549.json
...
```

Each file contains OMM orbital data used by Skyfield's `EarthSatellite.from_omm()` for sky position prediction.

## Behavior

1. Collect all NORAD catalog IDs from every file in `active_ids_dir`.
2. Authenticate with Space-Track using credentials from `space_track.env`.
3. Query the GP class for active payloads with epochs within the last 30 days:
   ```
   /basicspacedata/query/class/gp/decay_date/null-val/epoch/>now-30/object_type/payload/norad_cat_id/{ids}/format/json
   ```
4. Save each OMM record to `{tles_dir}/{NORAD_CAT_ID}.json`.
5. Assert that the number of downloaded files matches the number of requested IDs (prints a warning on mismatch).

## Rate limiting and caching

`fetch_omm` is wrapped with two decorators from `utils.py`:

| Decorator | Behavior |
|-----------|----------|
| `@once_per_hour_persistent` | Allows at most one live API call per hour; tracks last call in `last_omm_fetch_time.json` |
| `@disk_cache` | Caches API responses in `cache/` keyed by function arguments |

If called within an hour of the previous fetch, the script prints a wait message and returns cached data.

## Dependencies

- `requests`
- `python-dotenv`
- [`utils.py`](utils.md) — `once_per_hour_persistent`, `disk_cache`

## Notes

- Space-Track requires a free account. Credentials are stored in a private GitHub gist and fetched via `make init`.
- The once-per-hour limit is a conservative guard against Space-Track rate limits. Re-running `make tle` within the hour reuses cached results.
