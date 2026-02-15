from reedsolo import RSCodec

class ReedSolomon:
    def __init__(self, n, k):
        self.n = n
        self.k = k
        self.n_parity = n - k
        self.rsc = RSCodec(self.n_parity)

    def encode(self, blocks):
        if len(blocks) != self.k:
            raise ValueError(f"must input {self.k} data blocks")

        max_len = max(len(b) for b in blocks)
        padded = [b.ljust(max_len, b'\x00') for b in blocks]

        cols = []
        for i in range(max_len):
            col = bytes(p[i] for p in padded)
            enc_col = self.rsc.encode(col)
            cols.append(enc_col)

        out = [bytearray() for _ in range(self.n)]
        for col in cols:
            for i in range(self.n):
                out[i].append(col[i])

        return [bytes(b) for b in out]

    def decode(self, received_blocks):
        erase_pos = [i for i, b in enumerate(received_blocks) if b is None]
        
        valid = [b for b in received_blocks if b is not None]
        if not valid:
            return None

        max_len = max(len(b) for b in valid)
        n = self.n
        k = self.k

        data = []
        for b in received_blocks:
            if b is None:
                data.append(None)
            else:
                data.append(b.ljust(max_len, b'\x00'))

        restored_cols = []
        for i in range(max_len):
            col_bytes = bytes(
                data[j][i] if data[j] is not None else 0
                for j in range(n)
            )
            try:
                dec = self.rsc.decode(col_bytes, erase_pos=erase_pos)
                if isinstance(dec, (bytes, bytearray)):
                    fixed_col = dec
                else:
                    fixed_col = dec[0]
            except Exception:
                return None
            restored_cols.append(fixed_col)

        result = [bytearray() for _ in range(k)]
        for col in restored_cols:
            for i in range(k):
                result[i].append(col[i])

        return [bytes(r).rstrip(b'\x00') for r in result]

RS_3_1  = ReedSolomon(n=4,  k=3)
RS_10_4 = ReedSolomon(n=14, k=10)
RS_16_8 = ReedSolomon(n=24, k=16)