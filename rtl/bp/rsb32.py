class ReturnStackBuffer:
    """Simple circular return stack buffer."""

    def __init__(self, depth=32):
        self.depth = depth
        self.stack = [0] * depth
        self.sp = 0  # points to next free slot

    def push(self, addr):
        self.stack[self.sp] = addr & 0xFFFFFFFFFFFFFFFF
        self.sp = (self.sp + 1) % self.depth

    def pop(self):
        self.sp = (self.sp - 1) % self.depth
        return self.stack[self.sp]

    def top(self):
        return self.stack[(self.sp - 1) % self.depth]
