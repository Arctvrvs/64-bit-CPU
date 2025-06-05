class SmtArb:
    def __init__(self):
        self.last = 0

    def cycle(self, t0, t1):
        if t0 and t1:
            self.last ^= 1
        elif t0 or t1:
            self.last = 1 if t1 else 0
        g0 = t0 and (not t1 or not self.last)
        g1 = t1 and (not t0 or self.last)
        return g0, g1
