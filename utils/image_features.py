"""이미지 입력과 NumPy 배치 통계. 거래 테이블이나 파일을 변경하지 않는다."""

from pathlib import Path

import numpy as np
import pandas as pd

def prepare_image(pixels, image_size):
    """읽은 픽셀을 정규화된 float32 RGB 배열로 변환한다.

    작은 이미지는 호출 측에서 구분한다. 회색조는 3채널로 확장하고
    RGBA의 알파는 제외한다. 유한하지 않거나 범위를 벗어난 픽셀은 거부한다.
    """
    pixels = np.asarray(pixels)
    if pixels.ndim == 2:
        pixels = np.repeat(pixels[..., None], 3, axis=2)
    if pixels.ndim != 3 or pixels.shape[2] not in (1, 3, 4):
        raise ValueError("Expected grayscale, RGB or RGBA pixels.")
    if pixels.shape[2] == 1:
        pixels = np.repeat(pixels, 3, axis=2)
    pixels = pixels[..., :3]
    height, width = pixels.shape[:2]
    # 픽셀별 Python 반복 없이 같은 위치 규칙으로 32×32 표본을 고른다.
    rows = np.linspace(0, height - 1, image_size, dtype=int)
    columns = np.linspace(0, width - 1, image_size, dtype=int)
    sampled = pixels[rows[:, None], columns].astype(np.float32)
    if np.issubdtype(pixels.dtype, np.integer):
        sampled /= np.iinfo(pixels.dtype).max
    elif pixels.dtype.kind not in "fb":
        raise ValueError("Unsupported pixel dtype.")
    if not np.isfinite(sampled).all() or sampled.min() < 0 or sampled.max() > 1:
        raise ValueError("Pixels must be finite and within 0..1 after normalization.")
    return np.ascontiguousarray(sampled)

def extract_product_image_features(products, key, directory, prefix="image", image_size=32, batch_size=32):
    """고유 상품 표에서 피처 표와 최대 배치의 메모리 정보를 반환한다.

    directory 아래 <ID 앞 3자리>/<ID>.jpg를 읽는다. products의 key는
    비어 있지 않은 고유 문자열이어야 한다. image_size는 최소 원본 크기이자
    변환 크기, batch_size는 동시에 계산할 상품 수 상한이다.
    상태는 ok/missing/not_sampled/corrupt/too_small이며 실패 피처는 NaN이다.
    """
    from matplotlib.image import imread

    directory = Path(directory)
    if key not in products or products[key].isna().any() or products[key].duplicated().any():
        raise ValueError("Product keys must be present, non-null and unique.")
    for name, value in (("image_size", image_size), ("batch_size", batch_size)):
        if isinstance(value, bool) or not isinstance(value, int) or value < 1:
            raise ValueError(f"{name} must be a positive integer.")
    if not directory.is_dir():
        raise ValueError(f"Image directory not found: {directory}")
    keys = products[key]
    means = np.full(len(products), np.nan)
    stds = np.full(len(products), np.nan)
    statuses = np.full(len(products), "missing", dtype=object)
    batch_info = {}
    for start in range(0, len(products), batch_size):
        arrays, positions = [], []
        for position in range(start, min(start + batch_size, len(products))):
            product = products.iloc[position]
            # 추출 기록의 플래그로 원본 이미지 누락과 표본 미포함을 구분한다.
            if pd.notna(product.get("source_image_available")) and not product["source_image_available"]:
                continue
            if pd.notna(product.get("image_sampled")) and not product["image_sampled"]:
                statuses[position] = "not_sampled"
                continue
            identifier = str(keys.iloc[position])
            # 상품 ID를 파일명으로 쓰므로 경로 요소가 들어간 ID를 거부한다.
            if not identifier.isascii() or not identifier.isdecimal() or len(identifier) < 3:
                continue
            path = directory / identifier[:3] / f"{identifier}.jpg"
            if not path.is_file():
                continue
            try:
                pixels = np.asarray(imread(path))
                if pixels.ndim < 2:
                    raise ValueError("Image must have height and width.")
                if min(pixels.shape[:2]) < image_size:
                    statuses[position] = "too_small"
                    continue
                arrays.append(prepare_image(pixels, image_size))
            except (OSError, ValueError, SyntaxError):
                statuses[position] = "corrupt"
                continue
            positions.append(position)
            statuses[position] = "ok"
        if arrays:
            batch = np.stack(arrays)
            means[positions] = batch.mean(axis=(1, 2, 3))
            stds[positions] = batch.std(axis=(1, 2, 3), ddof=0)
            if batch.nbytes > batch_info.get("nbytes", 0):
                batch_info = {"shape": batch.shape, "dtype": str(batch.dtype),
                              "strides": batch.strides, "nbytes": batch.nbytes,
                              "c_contiguous": bool(batch.flags.c_contiguous)}
    features = pd.DataFrame({f"{prefix}_mean": means, f"{prefix}_std": stds,
                             f"{prefix}_status": statuses}, index=keys)
    return features, batch_info
