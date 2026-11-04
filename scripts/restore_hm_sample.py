"""Restore the H&M sample archive into the project's ignored data directory."""

import argparse
import hashlib
import json
import os
import re
import shutil
from filecmp import cmp
from pathlib import Path
from tempfile import TemporaryDirectory
from zipfile import BadZipFile, ZipFile


ROOT = Path(__file__).resolve().parents[1]
SAMPLE_DIR = ROOT / "data" / "raw" / "hm"
DRIVE_SOURCE = ROOT / "data" / "drive_source.json"
REQUIRED_FILES = {"transactions_sample.csv", "articles_sample.csv", "sample_manifest.json"}
IMAGE_PATH = re.compile(r"images/([0-9]{3})/\1[0-9]*\.jpg")


def sha256(path):
    digest = hashlib.sha256()
    with path.open("rb") as source:
        for chunk in iter(lambda: source.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def restore_sample(archive_path, destination):
    """Validate the archive and add its files without overwriting existing data."""
    destination = destination.resolve()
    destination.parent.mkdir(parents=True, exist_ok=True)
    with ZipFile(archive_path) as archive, TemporaryDirectory(dir=destination.parent) as temporary:
        names = archive.namelist()
        image_paths = set(names) - REQUIRED_FILES
        if (len(names) != len(set(names)) or not REQUIRED_FILES.issubset(names)
                or not image_paths or any(not IMAGE_PATH.fullmatch(name) for name in image_paths)):
            raise ValueError("The ZIP does not contain the expected H&M sample files.")

        manifest = json.loads(archive.read("sample_manifest.json"))
        if (not isinstance(manifest, dict)
                or manifest.get("source") != "h-and-m-personalized-fashion-recommendations"
                or manifest.get("sampled_images") != len(image_paths)):
            raise ValueError("The ZIP does not match its sample manifest.")

        staged = Path(temporary)
        for name in names:
            output = staged / name
            output.parent.mkdir(parents=True, exist_ok=True)
            with archive.open(name) as source, output.open("wb") as target:
                shutil.copyfileobj(source, target)

        for name in names:
            target = destination / name
            target.resolve().relative_to(destination)
            if target.exists() and not cmp(staged / name, target, shallow=False):
                raise FileExistsError(f"Existing file differs from the archive: {target}")

        for name in names:
            target = destination / name
            target.parent.mkdir(parents=True, exist_ok=True)
            # Publish a complete file without overwriting a concurrent restore.
            try:
                if os.name == "nt":
                    (staged / name).rename(target)
                else:
                    os.link(staged / name, target)
            except FileExistsError:
                if not cmp(staged / name, target, shallow=False):
                    raise
    return len(names)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--archive", type=Path, default=SAMPLE_DIR / "hm_sample.zip",
                        help="Path to the ZIP downloaded from Drive or exported by Kaggle")
    args = parser.parse_args()
    try:
        drive = json.loads(DRIVE_SOURCE.read_text(encoding="utf-8")) if DRIVE_SOURCE.exists() else {}
        if not isinstance(drive, dict):
            raise ValueError("The local Drive source must be a JSON object.")
        if not args.archive.is_file():
            message = f"Sample archive not found: {args.archive}. Pass its path with --archive."
            if drive.get("url"):
                message += f" Private Drive source: {drive['url']}"
            parser.error(message)
        if drive.get("sha256") and sha256(args.archive) != drive["sha256"]:
            raise ValueError("The ZIP checksum does not match the linked Drive sample.")
        count = restore_sample(args.archive, SAMPLE_DIR)
    except (BadZipFile, OSError, ValueError) as error:
        parser.error(str(error))
    print(f"Verified {count} H&M sample files in {SAMPLE_DIR}.")


if __name__ == "__main__":
    main()
