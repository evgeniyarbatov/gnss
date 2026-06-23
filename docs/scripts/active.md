# active.py

Filters each constellation catalog to satellites launched within the last 15 years, producing a list of active NORAD catalog IDs.

## Make target

```sh
make active
```

Depends on `ids/` being populated first (`make ids`).

## Usage

```sh
python scripts/active.py <ids_dir> <active_ids_dir>
```

Example:

```sh
python scripts/active.py ids/ ids/active/
```

## Inputs

| Argument | Default (Makefile) | Description |
|----------|-------------------|-------------|
| `ids_dir` | `ids/` | Full CelesTrak catalog files |
| `active_ids_dir` | `ids/active/` | Output directory |

## Outputs

One JSON file per constellation in `ids/active/`, each containing a flat array of integer NORAD catalog IDs:

```json
[
    62339,
    41549,
    39155
]
```

## Behavior

1. Read each `*.json` file in `ids_dir`.
2. Parse the launch year from `OBJECT_ID` (format `YYYY-NNNA`, e.g. `2024-123A` → year `2024`).
3. Keep satellites where `current_year - launch_year ≤ 15`.
4. Write the list of `NORAD_CAT_ID` values to the corresponding file in `active_ids_dir`.

## Constants

| Name | Value | Purpose |
|------|-------|---------|
| `SATELLITE_YEAR_CUTOFF` | `15` | Maximum age in years for a satellite to be considered active |

## Dependencies

None beyond the Python standard library.

## Notes

- The 15-year cutoff is a heuristic to reduce the number of TLE files downloaded and the search space during matching.
- Satellites without a parseable `OBJECT_ID` are silently skipped.