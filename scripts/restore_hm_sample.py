"""H&M 표본 복원 도구. 입력: ZIP과 선택적 Drive 검증 설정. 출력: 복원 파일 수·확인 로그. 부작용: Git 제외 data/에 기존 파일을 보호하며 표본을 복원한다."""

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
REQUIRED_FILES = {"transactions_sample.csv", "articles_sample.csv", "sample_manifest.json"}	# 거래·상품·추출 기록을 표본 ZIP의 필수 구성으로 고정한다.
IMAGE_PATH = re.compile(r"images/([0-9]{3})/\1[0-9]*\.jpg")	# 이미지 폴더와 상품 ID 앞 세 자리가 일치하는 경로만 허용한다.


def sha256(path):
    """입력: 읽을 파일의 Path 객체. 출력: SHA-256 16진수 문자열. 부작용: 파일을 순차 읽으며 읽기 오류를 전파한다."""
    digest = hashlib.sha256()
    with path.open("rb") as source:
        for chunk in iter(lambda: source.read(1024 * 1024), b""):	# 큰 ZIP을 한 번에 메모리에 올리지 않고 1 MiB씩 읽는다.
            digest.update(chunk)
    return digest.hexdigest()

def restore_sample(archive_path, destination):
    """입력: 표본 archive_path와 복원 destination 경로. 출력: 검증한 파일 수. 부작용: 임시 해제 후 없는 파일만 추가하며 다른 기존 파일은 예외로 보호한다."""
    destination = destination.resolve()
    destination.parent.mkdir(parents=True, exist_ok=True)
    with ZipFile(archive_path) as archive, TemporaryDirectory(dir=destination.parent) as temporary:	# 같은 부모 경로에 임시 해제하고 종료 시 임시 폴더를 정리한다.
        names = archive.namelist()
        image_paths = set(names) - REQUIRED_FILES	# 필수 세 파일을 제외한 항목은 모두 허용된 상품 이미지여야 한다.
        if (len(names) != len(set(names)) or not REQUIRED_FILES.issubset(names)
                or not image_paths or any(not IMAGE_PATH.fullmatch(name) for name in image_paths)):	# 중복·필수 파일 누락·이미지 없음·허용 밖 경로를 해제 전에 거부한다.
            raise ValueError("The ZIP does not contain the expected H&M sample files.")

        manifest = json.loads(archive.read("sample_manifest.json"))
        if (not isinstance(manifest, dict)
                or manifest.get("source") != "h-and-m-personalized-fashion-recommendations"
                or manifest.get("sampled_images") != len(image_paths)):	# 출처와 이미지 수가 추출 기록에 맞지 않으면 복원하지 않는다.
            raise ValueError("The ZIP does not match its sample manifest.")

        staged = Path(temporary)
        for name in names:
            output = staged / name
            output.parent.mkdir(parents=True, exist_ok=True)
            with archive.open(name) as source, output.open("wb") as target:
                shutil.copyfileobj(source, target)	# 최종 경로에 쓰기 전에 모든 파일을 임시 영역에 완전히 해제한다.

        for name in names:
            target = destination / name
            target.resolve().relative_to(destination)	# 기존 심볼릭 링크 등을 따라가도 복원 대상 바깥을 가리키지 않아야 한다.
            if target.exists() and not cmp(staged / name, target, shallow=False):	# 메타데이터가 아니라 실제 바이트를 비교하여 기존 데이터 충돌을 찾는다.
                raise FileExistsError(f"Existing file differs from the archive: {target}")

        for name in names:
            target = destination / name
            target.parent.mkdir(parents=True, exist_ok=True)

            try:
                if os.name == "nt":	# 윈도우의 이름 변경은 기존 대상 파일을 덮어쓰지 않는다.
                    (staged / name).rename(target)	# 완전히 기록한 파일을 최종 경로에 한 번에 배치한다.
                else:
                    os.link(staged / name, target)	# 다른 운영체제에서는 하드 링크로 기존 대상의 덮어쓰기를 막는다.
            except FileExistsError:	# 사전 검사 뒤 동시 복원으로 생긴 파일도 내용을 다시 확인한다.
                if not cmp(staged / name, target, shallow=False):	# 내용이 같은 기존 파일은 유지하고 다른 파일은 충돌로 처리한다.
                    raise
    return len(names)


def main():
    """입력: --archive 옵션과 선택적 Drive 설정 JSON. 출력: 없음. 부작용: 체크섬·ZIP을 검증해 표본을 복원하고 오류 시 CLI를 실패 종료한다."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--archive", type=Path, default=SAMPLE_DIR / "hm_sample.zip",
                        help="Path to the ZIP downloaded from Drive or exported by Kaggle")
    args = parser.parse_args()
    try:
        drive = json.loads(DRIVE_SOURCE.read_text(encoding="utf-8")) if DRIVE_SOURCE.exists() else {}	# 로컬 연결 설정이 없으면 경로·체크섬 추가 정보 없이 진행한다.
        if not isinstance(drive, dict):	# 설정은 키로 값을 찾을 수 있는 JSON 객체여야 한다.
            raise ValueError("The local Drive source must be a JSON object.")
        if not args.archive.is_file():	# ZIP이 없으면 실제 복원을 시작하지 않고 위치 안내를 반환한다.
            message = f"Sample archive not found: {args.archive}. Pass its path with --archive."
            if drive.get("url"):	# 설정에 있는 경우에만 사용자의 비공개 원본 위치를 안내한다.
                message += f" Private Drive source: {drive['url']}"
            parser.error(message)
        if drive.get("sha256") and sha256(args.archive) != drive["sha256"]:	# 제공된 기준 체크섬이 있으면 파일 전체의 무결성을 먼저 대조한다.
            raise ValueError("The ZIP checksum does not match the linked Drive sample.")
        count = restore_sample(args.archive, SAMPLE_DIR)
    except (BadZipFile, OSError, ValueError) as error:	# 손상 ZIP·파일 충돌·검증 실패를 일관된 명령행 오류로 전달한다.
        parser.error(str(error))
    print(f"Verified {count} H&M sample files in {SAMPLE_DIR}.")

if __name__ == "__main__":
    main()
