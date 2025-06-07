class ReturnStackBuffer:
    """Simple circular return stack buffer with optional coverage."""

    def __init__(self, depth=32, *, coverage=None):
        self.depth = depth
        self.stack = [0] * depth
        self.sp = 0  # points to next free slot
        self.count = 0
        self.coverage = coverage
        self.overflow_flag = False
        self.underflow_flag = False

    def push(self, addr):
        if self.count >= self.depth:
            self.overflow_flag = True
            if self.coverage:
                self.coverage.record_rsb_overflow()
        else:
            self.count = min(self.count + 1, self.depth)
        self.stack[self.sp] = addr & 0xFFFFFFFFFFFFFFFF
        self.sp = (self.sp + 1) % self.depth

    def pop(self):
        if self.count == 0:
            self.underflow_flag = True
            if self.coverage:
                self.coverage.record_rsb_underflow()
            return 0
        self.sp = (self.sp - 1) % self.depth
        self.count -= 1
        return self.stack[self.sp]

    def clear_flags(self):
        self.overflow_flag = False
        self.underflow_flag = False

    def top(self):
        if self.count == 0:
            return 0
        return self.stack[(self.sp - 1) % self.depth]
