# upload.py

Formats the matched lookup table and publishes a new version to the [Kaggle dataset](https://www.kaggle.com/datasets/evgenyarbatov/gnss-satellites/).

## Make target

```sh
make upload
```

Requires the [Kaggle CLI](https://github.com/Kaggle/kaggle-api) installed and authenticated (typically via `~/.kaggle/kaggle.json`), plus an existing `logs/matched.csv`.

## Usage

```sh
python scripts/upload.py <matches_file> <kaggle_file>
```

Example:

```sh
python scripts/upload.py logs/matched.csv kaggle/gnss.csv
```

## Inputs

| Argument | Default (Makefile) | Description |
|----------|-------------------|-------------|
| `matches_file` | `logs/matched.csv` | Svid-to-NORAD mapping |
| `kaggle_file` | `kaggle/gnss.csv` | Local dataset file to upload |

| Tool | Used for |
|------|----------|
| `kaggle` CLI | Dataset version upload (`kaggle datasets version`) |

## Outputs

1. **`kaggle/gnss.csv`** — formatted dataset:

   ```
   Svid,ConstellationType,NoradCatID,ConstellationName
   ```

2. **New Kaggle dataset version** — created via `api.dataset_create_version()` with message `"Update"`.

## Behavior

1. Read `matches_file`.
2. Convert each row to integers and add a human-readable `ConstellationName` (GPS, Glonass, QZSS, BeiDou, Galileo).
3. Write the result to `kaggle_file`.
4. Run `kaggle datasets version -p kaggle/ -m "Update"` to publish a new dataset version from the `kaggle/` directory (which includes `dataset-metadata.json`).

## Constellation name mapping

| `ConstellationType` | `ConstellationName` |
|---------------------|---------------------|
| 1 | GPS |
| 3 | Glonass |
| 4 | QZSS |
| 5 | BeiDou |
| 6 | Galileo |

## Dependencies

- `pandas`
- `kaggle` CLI (on `PATH`, authenticated separately from the Python `kaggle` package)

## Notes

- Rows that fail integer conversion are skipped with an error message.
- The Kaggle dataset metadata lives in `kaggle/dataset-metadata.json` and is not modified by this script.
