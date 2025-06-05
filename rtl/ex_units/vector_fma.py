class VectorFMA:
    """Simple 512-bit vector FMA model with 8 lanes."""
    def execute(self, a, b, c):
        assert len(a) == 8 and len(b) == 8 and len(c) == 8
        return [a[i] * b[i] + c[i] for i in range(8)]
