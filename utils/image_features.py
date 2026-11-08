"""이미지·상품 입력을 NumPy 피처와 배치·시간 진단으로 변환하며 입력 표와 파일을 변경하지 않는다."""

from pathlib import Path
from io import BytesIO
from statistics import median
from time import perf_counter

import numpy as np
import pandas as pd

def prepare_image(pixels, image_size):
    """픽셀 배열과 출력 크기를 받아 정규화된 연속 float32 RGB 배열을 반환한다.

    입력은 변경하지 않는다. 작은 이미지 판정은 호출자가 맡으며 회색조는 3채널로 확장한다.
    균일 격자로 위치를 선택하고 RGBA 알파는 제외하며 선택 픽셀의 비유한 값·범위 위반은 거부한다.
    """
    pixels = np.asarray(pixels)
    if pixels.ndim == 2:	# 채널 축이 없는 회색조를 RGB와 같은 연산 계약에 맞춘다.
        pixels = np.repeat(pixels[..., None], 3, axis=2)
    if pixels.ndim != 3 or pixels.shape[2] not in (1, 3, 4):	# 공간 축과 허용 채널 수가 맞지 않으면 후속 축약을 실행하지 않는다.
        raise ValueError("Expected grayscale, RGB or RGBA pixels.")
    if pixels.shape[2] == 1:	# 단일 채널을 세 번 복제해 채널 수를 통일한다.
        pixels = np.repeat(pixels, 3, axis=2)
    pixels = pixels[..., :3]	# 알파를 색상으로 평균내지 않으며 배경 합성은 별도로 수행하지 않는다.
    height, width = pixels.shape[:2]

    rows = np.linspace(0, height - 1, image_size, dtype=int)	# 보간 없이 균일 격자의 행 위치를 고르므로 해상도에 따른 정보 손실이 있다.
    columns = np.linspace(0, width - 1, image_size, dtype=int)	# 행·열을 독립 선택해 출력 크기를 고정하고 픽셀별 반복을 피한다.
    sampled = pixels[rows[:, None], columns].astype(np.float32)	# 고급 인덱싱과 자료형 변환으로 원본과 별도의 float32 표본을 만든다.
    if np.issubdtype(pixels.dtype, np.integer):	# 정수 자료형별 최댓값을 사용해 0~1 기준을 통일한다.
        sampled /= np.iinfo(pixels.dtype).max	# 예를 들어 uint8은 255로 나누며 원본 배열은 수정하지 않는다.
    elif pixels.dtype.kind not in "fb":	# 부동소수·불리언 외 자료형은 픽셀 의미를 확정할 수 없어 거부한다.
        raise ValueError("Unsupported pixel dtype.")
    if not np.isfinite(sampled).all() or sampled.min() < 0 or sampled.max() > 1:	# 선택된 픽셀의 유한성과 정규화 범위를 검사해 잘못된 통계를 막는다.
        raise ValueError("Pixels must be finite and within 0..1 after normalization.")
    return np.ascontiguousarray(sampled)	# 축약 연산의 메모리 접근을 일정하게 하되 필요한 경우 복사가 생긴다.

def advanced_image_statistics(batch, bins=8):
    """RGB 배치와 구간 수를 받아 이미지별 밝기 히스토그램·인접 절대차 평균을 반환한다.

    입력은 (N,H,W,3)의 유한한 0~1 배열이며 변경하지 않는다. 히스토그램은 이미지마다
    합이 1이고 마지막 구간은 밝기 1을 포함한다. 엣지는 수평·수직 인접 쌍의
    절대차 합/쌍 수이며 1×1에서는 0이다. 반환 형상은 (N,bins)와 (N,)이다.
    """
    batch = np.asarray(batch)
    if batch.ndim != 4 or batch.shape[-1] != 3 or min(batch.shape[:3]) < 1:	# 비어 있는 축이나 RGB가 아닌 배열은 통계의 분모·축 정의에 맞지 않는다.
        raise ValueError("Expected a nonempty (N,H,W,3) RGB batch.")
    if isinstance(bins, bool) or not isinstance(bins, int) or bins < 2:	# 불리언은 파이썬에서 정수 하위형이지만 구간 수로 허용하지 않는다.
        raise ValueError("bins must be an integer >= 2.")
    if not np.isfinite(batch).all() or batch.min() < 0 or batch.max() > 1:	# 구간 배정 전에 모든 픽셀의 정규화 계약을 확인한다.
        raise ValueError("Batch pixels must be finite and within 0..1.")
    gray = np.clip(batch @ np.array([.2126, .7152, .0722], dtype=np.float32), 0, 1)	# 선형화 없는 RGB 가중 근사로 물리 휘도와 구분하며 반올림 범위를 제한한다.
    count, height, width = gray.shape
    indices = np.minimum((gray * bins).astype(np.intp), bins - 1)	# 밝기 1도 마지막 구간에 포함되도록 인덱스 상한을 고정한다.
    offsets = np.arange(count)[:, None, None] * bins	# 이미지마다 구간 번호를 이동해 한 번의 bincount로 독립 집계를 만든다.
    histogram = np.bincount((indices + offsets).ravel(), minlength=count * bins).reshape(count, bins)	# 픽셀 반복 대신 평탄한 정수 인덱스를 벡터 집계한 뒤 이미지 축을 복원한다.
    histogram = histogram / (height * width)	# 픽셀 수로 나눠 이미지별 합이 1인 비율로 바꾼다.
    pairs = height * (width - 1) + (height - 1) * width	# 가로·세로 인접 쌍만 세며 이미지 사이 경계는 포함하지 않는다.
    difference = np.abs(np.diff(gray, axis=1)).sum(axis=(1, 2)) + np.abs(np.diff(gray, axis=2)).sum(axis=(1, 2))	# 두 공간 방향의 절대차를 더해 인접 대비의 크기를 요약한다.
    edge = difference / pairs if pairs else np.zeros(count)	# 1×1 이미지는 인접 쌍이 없어 0으로 정의해 0 나눗셈을 피한다.
    return histogram, edge


def extract_product_image_features(products, key, directory, prefix="image", image_size=32, batch_size=32,
                                   advanced=False, histogram_bins=8):
    """상품 표·키·이미지 경로·설정으로 피처 표와 최대 배치 버퍼 정보를 반환한다.

    directory 아래 <ID 앞 3자리>/<ID>.jpg를 읽으며 입력 표와 파일은 변경하지 않는다.
    products의 key는 결측 없는 고유 키다. image_size는 최소 원본 크기와 출력 크기이며
    batch_size는 상품 창의 상한이다. prefix는 출력 열 접두사, histogram_bins는 구간 수다.
    상태는 ok/missing/not_sampled/corrupt/too_small이며 실패 피처는 NaN으로 남긴다.
    advanced=True이면 같은 배치에 밝기 히스토그램·엣지를 추가하며 반환 표는 상품 키 인덱스다.
    """
    from matplotlib.image import imread

    directory = Path(directory)
    if key not in products or products[key].isna().any() or products[key].duplicated().any():	# 상품별 한 번 계산하고 결과를 키로 연결하려면 키의 유일성이 필요하다.
        raise ValueError("Product keys must be present, non-null and unique.")
    for name, value in (("image_size", image_size), ("batch_size", batch_size)):
        if isinstance(value, bool) or not isinstance(value, int) or value < 1:	# 배치와 공간 크기는 양의 정수여야 반복 범위와 배열 형상이 유효하다.
            raise ValueError(f"{name} must be a positive integer.")
    if not directory.is_dir():	# 경로 설정 오류를 모든 이미지의 누락으로 숨기지 않게 한다.
        raise ValueError(f"Image directory not found: {directory}")
    keys = products[key]
    means = np.full(len(products), np.nan)	# 실패와 미표본의 피처를 0으로 해석하지 않도록 결측으로 초기화한다.
    stds = np.full(len(products), np.nan)
    statuses = np.full(len(products), "missing", dtype=object)	# 기본 누락 상태를 두고 확인된 다른 원인만 별도로 기록한다.
    batch_info = {}
    if advanced:
        if isinstance(histogram_bins, bool) or not isinstance(histogram_bins, int) or histogram_bins < 2:	# 고급 피처를 켠 경우에만 해당 구간 수를 검증한다.
            raise ValueError("histogram_bins must be an integer >= 2.")
    advanced_values = {f"{prefix}_hist_{i}": np.full(len(products), np.nan)
                       for i in range(histogram_bins)} if advanced else {}	# 고급 피처를 사용하지 않으면 불필요한 추가 배열을 만들지 않는다.
    if advanced:
        advanced_values[f"{prefix}_edge_mean"] = np.full(len(products), np.nan)
    for start in range(0, len(products), batch_size):	# 상품 창 단위로 순회해 모든 이미지를 한 번에 메모리에 쌓지 않는다.
        arrays, positions = [], []	# 읽기에 성공한 배열과 원래 상품 위치를 함께 보관한다.
        for position in range(start, min(start + batch_size, len(products))):
            product = products.iloc[position]

            if pd.notna(product.get("source_image_available")) and not product["source_image_available"]:	# 추출 기록의 원본 누락은 표본 미포함과 구분해 기본 missing으로 남긴다.
                continue
            if pd.notna(product.get("image_sampled")) and not product["image_sampled"]:	# 표본에 의도적으로 넣지 않은 이미지를 읽기 실패로 집계하지 않는다.
                statuses[position] = "not_sampled"
                continue
            identifier = str(keys.iloc[position])

            if not identifier.isascii() or not identifier.isdecimal() or len(identifier) < 3:	# 경로 요소를 가진 식별자를 거부하고 숫자 파일명 규칙만 허용한다.
                continue
            path = directory / identifier[:3] / f"{identifier}.jpg"	# H&M 이미지의 앞 세 자리 하위 폴더 규칙에 맞춘다.
            if not path.is_file():	# 파일 부재는 손상 디코딩과 구분해 누락 상태로 남긴다.
                continue
            try:
                pixels = np.asarray(imread(path))	# 현재 경로는 파일별 순차 읽기·디코딩이며 픽셀 통계와 별도 비용이 든다.
                if pixels.ndim < 2:	# 공간 축이 없는 반환값은 정상 이미지로 처리하지 않는다.
                    raise ValueError("Image must have height and width.")
                if min(pixels.shape[:2]) < image_size:	# 작은 원본을 억지 확대하지 않고 크기 부족 상태로 분리한다.
                    statuses[position] = "too_small"
                    continue
                arrays.append(prepare_image(pixels, image_size))	# 축소·정규화한 작은 배열만 배치 목록에 보관한다.
            except (OSError, ValueError, SyntaxError):	# 파일 읽기·디코딩·픽셀 검증 오류를 상품별 손상 상태로 남긴다.
                statuses[position] = "corrupt"
                continue
            positions.append(position)	# 희소한 성공 이미지를 원래 상품 행에 되돌려 놓을 위치를 기록한다.
            statuses[position] = "ok"
        if arrays:	# 성공 이미지가 없는 창에서는 빈 stack을 호출하지 않는다.
            batch = np.stack(arrays)	# 형상이 같은 이미지들을 관측 축으로 쌓으며 별도 배치 버퍼가 만들어진다.
            means[positions] = batch.mean(axis=(1, 2, 3))	# 이미지 축은 남기고 높이·너비·채널 축만 평균낸다.
            stds[positions] = batch.std(axis=(1, 2, 3), ddof=0)	# 주어진 픽셀 전체의 퍼짐이므로 ddof=0이며 상품별 한 값이 남는다.
            if advanced:
                histogram, edges = advanced_image_statistics(batch, histogram_bins)	# 같은 전처리 배치를 재사용해 기본 피처와 고급 피처의 입력을 맞춘다.
                for index in range(histogram_bins):
                    advanced_values[f"{prefix}_hist_{index}"][positions] = histogram[:, index]	# 구간 반복은 출력 열 배치용이며 픽셀별 파이썬 반복은 아니다.
                advanced_values[f"{prefix}_edge_mean"][positions] = edges
            if batch.nbytes > batch_info.get("nbytes", 0):	# 최대 배치의 실제 버퍼 정보를 남기며 전체 프로세스 메모리를 뜻하지는 않는다.
                batch_info = {"shape": batch.shape, "dtype": str(batch.dtype),
                              "strides": batch.strides, "nbytes": batch.nbytes,
                              "c_contiguous": bool(batch.flags.c_contiguous)}
    features = pd.DataFrame({f"{prefix}_mean": means, f"{prefix}_std": stds,
                             f"{prefix}_status": statuses, **advanced_values}, index=keys)	# 상품 키를 인덱스로 사용해 거래 표에 안정적으로 매핑할 수 있게 한다.
    return features, batch_info


def profile_jpeg_stages(paths, image_size=32, repeats=3):
    """JPEG 경로 목록·출력 크기·반복 수로 단계별 시간 중앙값을 초 단위 사전으로 반환한다.

    파일은 순차로 읽되 변경하지 않는다. 워밍업에서 파일·메모리 디코딩의 전처리 배열을 대조한다.
    파일 읽기는 운영체제 캐시 상태에 영향을 주며 측정값은 실행 환경과 워밍업 조건에 의존한다.
    """
    from matplotlib.image import imread

    paths = tuple(map(Path, paths))	# 경로 입력을 고정해 워밍업과 반복 계측이 같은 이미지 목록을 사용한다.
    if not paths or repeats < 1:	# 빈 목록과 반복 없는 계측은 유효한 중앙값을 만들 수 없다.
        raise ValueError("Provide JPEG paths and at least one repetition.")
    for path in paths:
        buffered = imread(BytesIO(path.read_bytes()), format="jpeg")	# 워밍업은 파일 캐시와 디코더 초기화 비용의 영향을 바꿀 수 있다.
        np.testing.assert_array_equal(prepare_image(buffered, image_size),
                                      prepare_image(imread(path), image_size))	# 계측을 위해 읽기 경로를 나눠도 피처 입력이 동일한지 검증한다.

    timings = {"Read bytes": [], "Decode JPEG": [], "Prepare pixels": []}	# 읽기·메모리 디코딩·픽셀 전처리의 시간을 서로 다른 집계로 보관한다.
    for _ in range(repeats):
        reading = decoding = preparing = 0.0
        for path in paths:
            start = perf_counter()	# 각 이미지에서 고해상도 단조 시계로 단계 경계를 측정한다.
            encoded = path.read_bytes()	# 압축된 파일 바이트 읽기만 첫 구간에 포함한다.
            read_at = perf_counter()
            pixels = imread(BytesIO(encoded), format="jpeg")	# 이미 읽은 메모리 바이트로 디코딩해 파일 읽기 구간과 분리한다.
            decoded_at = perf_counter()
            prepare_image(pixels, image_size)	# 격자 선택·정규화·연속화만 마지막 구간으로 측정한다.
            reading += read_at - start
            decoding += decoded_at - read_at
            preparing += perf_counter() - decoded_at	# 각 반복에서는 이미지별 시간을 합산해 전체 목록의 단계 시간을 얻는다.
        timings["Read bytes"].append(reading)
        timings["Decode JPEG"].append(decoding)
        timings["Prepare pixels"].append(preparing)
    return {stage: median(seconds) for stage, seconds in timings.items()}	# 단계별 중앙값의 합이 별도 전체 실행 시간의 중앙값과 같다고 보장하지 않는다.
