import sys

from gdown.download_folder import download_folder

GOOGLE_DRIVE_ID = "1T_Cbos3dsvlx6DYsh8cFFh7GJYG3G5Qr"


def main(logs_dir: str) -> None:
    # Public folders must be fetched without cookies; otherwise Google
    # redirects to ServiceLogin and gdown sees an empty folder.
    downloaded = download_folder(
        id=GOOGLE_DRIVE_ID,
        output=logs_dir,
        use_cookies=False,
    )
    if not downloaded:
        raise RuntimeError(
            "No files downloaded from Google Drive folder "
            f"{GOOGLE_DRIVE_ID}. Check that the folder is shared as "
            "'Anyone with the link'."
        )


if __name__ == "__main__":
    main(*sys.argv[1:])
