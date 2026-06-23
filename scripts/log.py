import gdown
import sys

GOOGLE_DRIVE_ID = "1T_Cbos3dsvlx6DYsh8cFFh7GJYG3G5Qr"


def main(logs_dir):
    gdown.download_folder(id=GOOGLE_DRIVE_ID, output=logs_dir)


if __name__ == "__main__":
    main(*sys.argv[1:])
