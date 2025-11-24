VENV_PATH := .venv
PYTHON := $(VENV_PATH)/bin/python
PIP := $(VENV_PATH)/bin/pip
REQUIREMENTS := requirements.txt

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
	@python3 -m venv $(VENV_PATH)

install: venv
	@$(PIP) install --disable-pip-version-check -q --upgrade pip
	@$(PIP) install --disable-pip-version-check -q -r $(REQUIREMENTS)

ids:
	@$(PYTHON) scripts/ids.py $(CONSTELLATIONS_FILE) $(IDS_DIR);

active:
	@$(PYTHON) scripts/active.py $(IDS_DIR) $(ACTIVE_IDS_DIR);

tle:
	@$(PYTHON) scripts/tle.py $(ACTIVE_IDS_DIR) $(TLES_DIR);

parquet:
	@$(PYTHON) scripts/parquet.py;

log:
	@$(PYTHON) scripts/log.py $(LOGS_DIR);

filter:
	@$(PYTHON) scripts/filter.py $(LOGS_DIR) $(FILTERED_LOGS_DIR);

match: filter
	@$(PYTHON) scripts/match.py \
	$(ACTIVE_IDS_DIR) \
	$(TLES_DIR) \
	$(FILTERED_LOGS_DIR) \
	$(MATCHES_FILE);

upload:
	source $(VENV_PATH)/bin/activate && \
	python3 scripts/upload.py $(MATCHES_FILE) $(KAGGLE_FILE);

stats:
	@$(PYTHON) scripts/stats.py \
	$(KAGGLE_FILE) \
	$(TLES_DIR)

.PHONY: init ids active tle log filter match verify upload stats