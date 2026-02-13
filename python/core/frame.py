#core/frame.py
import struct
import zlib
from .consts import HEADER_SIZE

def build_frame(
    ver: int,
    cmd: int,
    conn_id: int,
    seq: int,
    payload: bytes,
    encrypt_mode: int,
    compress_mode: int
) -> bytes:
    payload_len = len(payload)

    header_part = struct.pack(
        "!HHIIHBB",
        ver,
        cmd,
        conn_id,
        seq,
        payload_len,
        encrypt_mode,
        compress_mode
    )

    checksum = zlib.crc32(header_part + payload) & 0xFFFFFFFF
    header = header_part + struct.pack("!I", checksum)

    return header + payload

def parse_frame(frame: bytes) -> dict:
    if len(frame) < HEADER_SIZE:
        raise ValueError("invalid frame: too short")

    header = frame[:HEADER_SIZE]
    payload = frame[HEADER_SIZE:]

    header_part = header[:16]
    checksum_recv = struct.unpack("!I", header[16:20])[0]

    checksum_calc = zlib.crc32(header_part + payload) & 0xFFFFFFFF
    if checksum_calc != checksum_recv:
        raise ValueError("checksum mismatch")

    ver, cmd, conn_id, seq, payload_len, encrypt_mode, compress_mode \
        = struct.unpack("!HHIIHBB", header_part)

    return {
        "ver": ver,
        "cmd": cmd,
        "conn_id": conn_id,
        "seq": seq,
        "payload_len": payload_len,
        "encrypt_mode": encrypt_mode,
        "compress_mode": compress_mode,
        "payload": payload
    }