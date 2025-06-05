class VectorFMA512:
    """Simple 5-cycle 512-bit fused multiply-add unit model."""

    STAGES = 5

    def __init__(self):
        self.val_pipe = [False] * self.STAGES
        self.res_pipe = [0] * self.STAGES

    def step(self, valid, src1, src2, src3):
        # propagate pipeline first
        for i in range(self.STAGES - 1, 0, -1):
            self.val_pipe[i] = self.val_pipe[i - 1]
            self.res_pipe[i] = self.res_pipe[i - 1]
        # compute new stage 0
        if valid:
            self.val_pipe[0] = True
            self.res_pipe[0] = ((src1 & ((1 << 512) - 1)) * (src2 & ((1 << 512) - 1)) + (src3 & ((1 << 512) - 1))) & ((1 << 512) - 1)
        else:
            self.val_pipe[0] = False
            self.res_pipe[0] = 0
        return self.val_pipe[-1], self.res_pipe[-1]
