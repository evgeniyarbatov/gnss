# ids.py

Fetches the full NORAD satellite catalog for each GNSS constellation from [CelesTrak](https://celestrak.org).

## Make target

```sh
make ids
```

## Usage

```sh
python scripts/ids.py <constellations_file> <ids_dir>
```

Example:

```sh
python scripts/ids.py constellations.json ids/
```

## Inputs

| Argument | Default (Makefile) | Description |
|----------|-------------------|-------------|
| `constellations_file` | `constellations.json` | JSON array of constellation search names |
| `ids_dir` | `ids/` | Output directory for catalog files |

`constellations.json` lists six GNSS groups: `qzs`, `beidou`, `glonass`, `navstar`, `galileo`, `sbas`.

## Outputs

One JSON file per constellation in `ids/`:

```
ids/navstar.json
ids/glonass.json
ids/galileo.json
ids/beidou.json
ids/qzs.json
ids/sbas.json
```

Each file contains an array of satellite objects from CelesTrak's GP catalog, including `NORAD_CAT_ID`, `OBJECT_ID`, `OBJECT_NAME`, and orbital elements.

## Behavior

1. Load constellation names from the input JSON file.
2. For each name, request `https://celestrak.org/NORAD/elements/gp.php?NAME={name}&FORMAT=json-pretty` — except `sbas`, which uses `GROUP={name}` instead, since SBAS satellites (EGNOS, WAAS, GAGAN, ...) don't share a common name substring the way GPS/GLONASS/etc. satellites do.
3. Save the response to `{ids_dir}/{name}.json`.
4. Sleep 1 second between requests to avoid hammering CelesTrak.

## Dependencies

- `requests`

## Notes

- This step downloads the **full** catalog per constellation. The next step (`active.py`) narrows it to recently launched satellites.
- Failed HTTP requests are logged but do not halt the pipeline; the constellation file is simply skipped.