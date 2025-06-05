class L1ICache:
    """Simple in-memory model of the L1 instruction cache with TLB lookup."""
    def __init__(self, tlb_l1=None, tlb_l2=None, walker=None):
        from rtl.mmu import TlbL1, TlbL2, PageWalker8
        self.mem = {}
        self.tlb_l1 = tlb_l1 if tlb_l1 is not None else TlbL1()
        self.tlb_l2 = tlb_l2 if tlb_l2 is not None else TlbL2()
        self.walker = walker if walker is not None else PageWalker8()

    def _translate(self, va):
        hit, pa, fault = self.tlb_l1.lookup(va, perm='x')
        if hit:
            return pa, fault
        hit, pa, fault = self.tlb_l2.lookup(va, perm='x')
        if hit:
            self.tlb_l1.refill(va, pa, perm='x')
            return pa, fault
        pa, fault = self.walker.walk(va, perm='x')
        if not fault:
            self.tlb_l2.refill(va, pa, perm='x')
            self.tlb_l1.refill(va, pa, perm='x')
        return pa, fault

    def load(self, addr, data):
        """Load a 32-bit instruction word at the given physical address."""
        self.mem[addr & ~0x3] = data & 0xFFFFFFFF

    def fetch(self, addr):
        """Translate *addr* and return the instruction word or 0."""
        pa, fault = self._translate(addr)
        if fault:
            return 0
        return self.mem.get(pa & ~0x3, 0)
