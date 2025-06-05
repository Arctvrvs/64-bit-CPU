class L1DCache:
    """Simple in-memory model of the L1 data cache."""
    def __init__(self):
        self.mem = {}

    def write(self, addr, data, wstrb=0xFF):
        """Write 64-bit *data* to *addr* with byte strobe mask *wstrb*."""
        word_addr = addr & ~0x7
        val = self.mem.get(word_addr, 0)
        for i in range(8):
            if (wstrb >> i) & 1:
                mask = 0xFF << (8 * i)
                val = (val & ~mask) | (data & mask)
        self.mem[word_addr] = val & 0xFFFFFFFFFFFFFFFF

    def read(self, addr):
        """Return the 64-bit value stored at *addr* or 0."""
        word_addr = addr & ~0x7
        return self.mem.get(word_addr, 0)
