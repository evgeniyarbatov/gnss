# log.py

Downloads GNSSLogger observation files from a Google Drive folder into the local `logs/` directory.

## Make target

```sh
make log
```

## Usage

```sh
python scripts/log.py <logs_dir>
```

Example:

```sh
python scripts/log.py logs/
```

## Inputs

| Argument | Default (Makefile) | Description |
|----------|-------------------|-------------|
| `logs_dir` | `logs/` | Local directory for downloaded `.txt` files |

| Constant | Value | Purpose |
|----------|-------|---------|
| `GOOGLE_DRIVE_ID` | `1T_Cbos3dsvlx6DYsh8cFFh7GJYG3G5Qr` | Source Google Drive folder |

## Outputs

Raw GNSSLogger `.txt` files in `logs/`:

```
logs/gnss_log_2025_05_25_16_20_34.txt
logs/gnss_log_2025_03_06_06_56_19.txt
...
```

## Behavior

Calls `gdown.download_folder()` to sync the entire Google Drive folder to the local `logs_dir`. Existing files may be skipped depending on `gdown` behavior.

## Log format

GNSSLogger writes comma-separated rows with a `#` header comment block. Relevant `Status` row fields used downstream:

| Field | Description |
|-------|-------------|
| `UnixTimeMillis` | Observation timestamp |
| `ConstellationType` | Android constellation enum (1=GPS, 3=GLONASS, etc.) |
| `Svid` | Satellite vehicle ID within the constellation |
| `AzimuthDegrees` | Reported azimuth |
| `ElevationDegrees` | Reported elevation |
| `BasebandCn0DbHz` | Signal strength (filtered in `utils.read_gnss_log`) |

## Dependencies

- `gdown`

## Notes

- The Google Drive folder ID is hardcoded. To use your own logs, replace `GOOGLE_DRIVE_ID` or place `.txt` files directly in `logs/`.
- GNSSLogger must have **Status logging** enabled on the Android device.
