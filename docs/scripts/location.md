# location.py

Provides observer coordinates for sky-position calculations. Values are read from environment variables set by the Makefile.

Not invoked directly via Make. Imported by `match.py`, `verify.py`, and `stats.py`.

## Environment variables

| Variable | Makefile default | Description |
|----------|-----------------|-------------|
| `LAT` | `20.99484734661426` | Observer latitude (Hanoi area) |
| `LON` | `105.86761269335307` | Observer longitude |
| `TIMEZONE` | `Asia/Ho_Chi_Minh` | IANA timezone for timestamp conversion |

## Exports

```python
LAT = float(os.environ["LAT"])
LON = float(os.environ["LON"])
TIMEZONE = os.environ["TIMEZONE"]
```

All three are evaluated at import time. Missing variables raise `KeyError`.

## Makefile integration

The Makefile defines location once and injects it via `GNSS_ENV`:

```makefile
LAT = 20.99484734661426
LON = 105.86761269335307
TIMEZONE = Asia/Ho_Chi_Minh

GNSS_ENV = LAT=$(LAT) LON=$(LON) TIMEZONE=$(TIMEZONE)
```

Targets that need location prefix their Python invocation:

```makefile
@$(GNSS_ENV) $(PYTHON) scripts/match.py ...
```

## Usage outside Make

When running location-aware scripts manually, export the variables first:

```sh
export LAT=20.99484734661426
export LON=105.86761269335307
export TIMEZONE=Asia/Ho_Chi_Minh
python scripts/match.py ids/active/ tles/ logs/filtered/ logs/matched.csv
```

## Notes

- TLE-predicted azimuth and elevation depend entirely on the observer position. Change these values to match where GNSS logs were recorded.
- This module is separate from [`utils.py`](utils.md) so that scripts like `tle.py` can import shared utilities without requiring location environment variables.
