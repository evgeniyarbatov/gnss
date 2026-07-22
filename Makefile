# Uses uv (https://docs.astral.sh/uv) for dependency management — uv sync creates/updates .venv; run commands via uv run, no manual activation.

LAT = 10.78704710227992
LON = 106.70711329480078
TIMEZONE = Asia/Ho_Chi_Minh

GNSS_ENV = LAT=$(LAT) LON=$(LON) TIMEZONE=$(TIMEZONE)

CONSTELLATIONS_FILE = constellations.json

SPACE_TRACK_GIST_ID = 6a39486eb8aefc2f8db3c07b300481d6
KAGGLE_GIST_ID = 464510d59193bab4351f62baa018e3e9

IDS_DIR = ids
ACTIVE_IDS_DIR = ids/active

TLES_DIR = tles

LOGS_DIR = logs
FILTERED_LOGS_DIR = logs/filtered

MATCHES_FILE = logs/matched.csv
VERIFIED_FILE = logs/verified.csv

KAGGLE_FILE = kaggle/gnss.csv

all: install init ids active tle log filter match verify upload stats

init:
	@gh gist view $(SPACE_TRACK_GIST_ID) --raw > space_track.env
	@gh gist view $(KAGGLE_GIST_ID) --raw > kaggle.env

install:
	@uv sync --dev

test: install
	@uv run python -m unittest discover -s tests -p 'test_*.py' -v

ids: install
	@uv run python scripts/ids.py $(CONSTELLATIONS_FILE) $(IDS_DIR);

active: install
	@uv run python scripts/active.py $(IDS_DIR) $(ACTIVE_IDS_DIR);

tle: install
	@uv run python scripts/tle.py $(ACTIVE_IDS_DIR) $(TLES_DIR);

parquet: install
	@uv run python scripts/parquet.py;

log: install
	@uv run python scripts/log.py $(LOGS_DIR);

filter: install
	@uv run python scripts/filter.py $(LOGS_DIR) $(FILTERED_LOGS_DIR);

match: install filter
	@$(GNSS_ENV) uv run python scripts/match.py \
	$(ACTIVE_IDS_DIR) \
	$(TLES_DIR) \
	$(FILTERED_LOGS_DIR) \
	$(MATCHES_FILE);

verify: install match
	@$(GNSS_ENV) uv run python scripts/verify.py \
	$(FILTERED_LOGS_DIR) \
	$(TLES_DIR) \
	$(MATCHES_FILE) \
	$(VERIFIED_FILE);

upload: install
	@uv run python scripts/upload.py $(MATCHES_FILE) $(KAGGLE_FILE);

stats: install
	@$(GNSS_ENV) uv run python scripts/stats.py \
	$(KAGGLE_FILE) \
	$(TLES_DIR)

.PHONY: init test ids active tle log filter match verify upload stats lock help

lock:
	uv lock

help:
	@echo "install - uv sync --dev"
	@echo "test    - run unit tests"
	@echo "init    - fetch space_track.env / kaggle.env from gh gists"
	@echo "ids     - resolve constellation ids"
	@echo "active  - filter to active satellite ids"
	@echo "tle     - fetch TLEs for active ids"
	@echo "log     - fetch GNSS logs"
	@echo "filter  - filter logs"
	@echo "match   - match logs to satellites"
	@echo "verify  - verify matches"
	@echo "upload  - upload matches to Kaggle"
	@echo "stats   - print stats"
	@echo "lock    - refresh uv.lock"
