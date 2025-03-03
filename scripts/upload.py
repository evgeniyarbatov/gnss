import sys
import os

import kaggle
from kaggle.api.kaggle_api_extended import KaggleApi

def main(matches_file):
	api = KaggleApi()
	api.authenticate()

	api.dataset_create_version(
		os.path.dirname(matches_file),
		'Update',
	)

if __name__ == "__main__":
	main(*sys.argv[1:])