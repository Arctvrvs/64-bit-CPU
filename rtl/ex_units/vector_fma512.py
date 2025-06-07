class VectorFMA512:
    """Simple 5-cycle 512-bit fused multiply-add unit model."""

    STAGES = 5

    def __init__(self):
        self.val_pipe = [False] * self.STAGES
        self.res_pipe = [0] * self.STAGES

    def step(self, valid, src1, src2, src3, mask=0xFF):
        # propagate pipeline first
        for i in range(self.STAGES - 1, 0, -1):
            self.val_pipe[i] = self.val_pipe[i - 1]
            self.res_pipe[i] = self.res_pipe[i - 1]
        # compute new stage 0
        if valid:
            self.val_pipe[0] = True
            res = 0
            for lane in range(8):
                a = (src1 >> (lane * 64)) & ((1 << 64) - 1)
                b = (src2 >> (lane * 64)) & ((1 << 64) - 1)
                c = (src3 >> (lane * 64)) & ((1 << 64) - 1)
                prod = (a * b + c) & ((1 << 64) - 1)
                if (mask >> lane) & 1:
                    res |= prod << (lane * 64)
                else:
                    res |= c << (lane * 64)
            self.res_pipe[0] = res
        else:
            self.val_pipe[0] = False
            self.res_pipe[0] = 0
        return self.val_pipe[-1], self.res_pipe[-1]
