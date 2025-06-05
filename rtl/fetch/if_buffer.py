class IFBuffer16:
    """Simple FIFO storing up to 16 instruction pairs."""

    def __init__(self):
        self.buffer = []
        self.capacity = 16

    def enqueue(self, inst_pair):
        if len(self.buffer) < self.capacity:
            self.buffer.append(inst_pair & 0xFFFFFFFFFFFFFFFF)
            return True
        return False

    def dequeue(self):
        if self.buffer:
            return self.buffer.pop(0)
        return None

    def count(self):
        return len(self.buffer)
