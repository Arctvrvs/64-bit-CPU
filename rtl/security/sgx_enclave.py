class SGXEnclave:
    """Python model matching the sgx_enclave stub."""
    def __init__(self):
        self.epcm = set()
        self.active = False

    def _page(self, addr: int) -> int:
        return (addr >> 8) & 0xFF

    def ecreate(self, addr: int):
        self.epcm.add(self._page(addr))

    def eadd(self, addr: int, data: int):
        self.epcm.add(self._page(addr))
        # data ignored in the stub

    def einit(self):
        pass

    def eenter(self):
        self.active = True

    def eexit(self):
        self.active = False

    def access(self, addr: int) -> bool:
        if self.active and self._page(addr) not in self.epcm:
            return True
        return False
