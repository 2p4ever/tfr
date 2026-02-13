import struct
from typing import List, Optional
from .consts import *

def fec_encode(blocks: List[bytes]) -> List[bytes]:
    data_blocks = blocks[:FEC_DATA_NUM]
    while len(data_blocks) < FEC_DATA_NUM:
        data_blocks.append(b'')

    max_len = max(len(b) for b in data_blocks)

    padded_blocks = [b + b'\x00' * (max_len - len(b)) for b in data_blocks]

    parity = bytearray(max_len)
    for i in range(max_len):
        val = 0
        for b in padded_blocks:
            val ^= b[i]
        parity[i] = val

    return [*data_blocks, bytes(parity)]

def fec_decode(blocks: List[Optional[bytes]]) -> Optional[bytes]:
    missing = [i for i, b in enumerate(blocks) if b is None]
    if len(missing) != 1:
        return None

    lost_idx = missing[0]
    if lost_idx >= FEC_DATA_NUM:
        return None

    max_len = 0
    for b in blocks:
        if b is not None:
            max_len = max(max_len, len(b))

    recovered = bytearray()
    for i in range(max_len):
        val = 0
        for j, b in enumerate(blocks):
            if j == lost_idx:
                continue
            if b is not None and i < len(b):
                val ^= b[i]
        recovered.append(val)

    return bytes(recovered).rstrip(b'\x00')