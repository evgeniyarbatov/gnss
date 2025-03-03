import gdown
import sys

GOOGLE_DRIVE_ID = "11WMO-rdsKazhKZ1nlzmbigxZuWrzuI_R"

def main(logs_dir):
    gdown.download_folder(id=GOOGLE_DRIVE_ID, output=logs_dir)

if __name__ == "__main__":
    main(*sys.argv[1:])