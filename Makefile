VENV_PATH := .venv
PYTHON := $(VENV_PATH)/bin/python
PIP := $(VENV_PATH)/bin/pip
REQUIREMENTS := requirements.txt

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

all: venv install init ids active tle log filter match verify upload stats

init:
	@gh gist view $(SPACE_TRACK_GIST_ID) --raw > space_track.env
	@gh gist view $(KAGGLE_GIST_ID) --raw > kaggle.env

venv:
	@uv venv $(VENV_PATH)

install: venv
	@uv pip install -q -r $(REQUIREMENTS)

ids: install
	@$(PYTHON) scripts/ids.py $(CONSTELLATIONS_FILE) $(IDS_DIR);
active: install
	@$(PYTHON) scripts/active.py $(IDS_DIR) $(ACTIVE_IDS_DIR);
tle: install
	@$(PYTHON) scripts/tle.py $(ACTIVE_IDS_DIR) $(TLES_DIR);
parquet: install
	@$(PYTHON) scripts/parquet.py;
log: install
	@$(PYTHON) scripts/log.py $(LOGS_DIR);
filter: install
	@$(PYTHON) scripts/filter.py $(LOGS_DIR) $(FILTERED_LOGS_DIR);
match: install filter
	@$(GNSS_ENV) $(PYTHON) scripts/match.py \
	$(ACTIVE_IDS_DIR) \
	$(TLES_DIR) \
	$(FILTERED_LOGS_DIR) \
	$(MATCHES_FILE);
verify: install match
	@$(GNSS_ENV) $(PYTHON) scripts/verify.py \
	$(FILTERED_LOGS_DIR) \
	$(TLES_DIR) \
	$(MATCHES_FILE) \
	$(VERIFIED_FILE);
upload: install
	@$(PYTHON) scripts/upload.py $(MATCHES_FILE) $(KAGGLE_FILE);
stats: install
	@$(GNSS_ENV) $(PYTHON) scripts/stats.py \
	$(KAGGLE_FILE) \
	$(TLES_DIR)
.PHONY: init ids active tle log filter match verify upload stats

cleanvenv:
	@rm -rf $(VENV_PATH)
