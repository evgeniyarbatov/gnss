# filter.py

Reduces raw GNSSLogger logs to a single representative observation per satellite per log session.

## Make target

```sh
make filter
```

## Usage

```sh
python scripts/filter.py <logs_dir> <filtered_logs_dir>
```

Example:

```sh
python scripts/filter.py logs/ logs/filtered/
```

## Inputs

| Argument | Default (Makefile) | Description |
|----------|-------------------|-------------|
| `logs_dir` | `logs/` | Raw GNSSLogger `.txt` files |
| `filtered_logs_dir` | `logs/filtered/` | Output directory |

## Outputs

One CSV per input log file in `logs/filtered/`:

```
Svid,ConstellationType,ConstellationName,UnixTimeMillis,AzimuthDegrees,ElevationDegrees
```

## Behavior

For each `.txt` file in `logs_dir`:

1. Parse with [`read_gnss_log`](utils.md) (applies signal strength filter: `BasebandCn0DbHz > 25`).
2. Group by `(Svid, ConstellationType, ConstellationName)`.
3. Keep the **first** row per group (earliest observation in the log).
4. Write the result as a CSV to `filtered_logs_dir` with the same filename.

## Dependencies

- [`utils.py`](utils.md) — `read_gnss_log`

## Notes

- This step discards temporal data within a session. `match.py` uses only the first snapshot per satellite, while `verify.py` reads the full raw logs separately for time-series validation.
- Weak-signal rows are already removed by `read_gnss_log` before grouping.