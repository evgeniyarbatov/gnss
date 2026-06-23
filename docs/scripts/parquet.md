# parquet.py

Utility script that consolidates all individual TLE JSON files into a single Parquet file for bulk analysis.

## Make target

```sh
make parquet
```

Not part of the default `make all` pipeline.

## Usage

```sh
python scripts/parquet.py
```

No command-line arguments. The script uses a hardcoded `tles_dir = "tles"` and writes to `tles/tles.parquet`.

## Inputs

All `*.json` files in `tles/`:

```
tles/62339.json
tles/41549.json
...
```

## Outputs

```
tles/tles.parquet
```

A single Parquet file containing one row per satellite OMM record.

## Behavior

1. Iterate over every `.json` file in `tles/`.
2. Load each OMM object and append to a list.
3. Convert to a pandas DataFrame.
4. Write to Parquet using the PyArrow engine.

Prints a summary on completion:

```
Saved 412 TLEs to tles/tles.parquet
```

## Dependencies

- `pandas`, `pyarrow`

## Notes

- This is a standalone data export tool with no integration into the matching pipeline.
- Paths are hardcoded; edit the script to change input/output locations.