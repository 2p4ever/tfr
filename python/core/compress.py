# core/compress.py
# 依赖安装：pip install python-snappy lz4
import zlib
import snappy
import lz4.frame as lz4
from .consts import COMPRESS_NONE, COMPRESS_ZLIB, COMPRESS_SNAPPY, COMPRESS_LZ4


# -----------------------------------------------------------------------------
# Compress/Decompress
# -----------------------------------------------------------------------------
def compress(data: bytes, compress_type: int) -> bytes:
    if compress_type == COMPRESS_NONE:
        return data
    elif compress_type == COMPRESS_ZLIB:
        return zlib.compress(data, level=6)
    elif compress_type == COMPRESS_SNAPPY:
        return snappy.compress(data)
    elif compress_type == COMPRESS_LZ4:
        return lz4.compress(data, compression_level=3)
    else:
        raise ValueError(f"compress: unsupported type {compress_type}")


def decompress(data: bytes, compress_type: int) -> bytes:
    if compress_type == COMPRESS_NONE:
        return data
    elif compress_type == COMPRESS_ZLIB:
        try:
            return zlib.decompress(data)
        except zlib.error:
            raise ValueError("compress: zlib decompress failed")
    elif compress_type == COMPRESS_SNAPPY:
        try:
            return snappy.decompress(data)
        except snappy.InvalidCompressedDataError:
            raise ValueError("compress: snappy decompress failed")
    elif compress_type == COMPRESS_LZ4:
        try:
            return lz4.decompress(data)
        except lz4.LZ4FrameError:
            raise ValueError("compress: lz4 decompress failed")
    else:
        raise ValueError(f"compress: unsupported type {compress_type}")