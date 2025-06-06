class TlbL1:
    """Simple L1 TLB model with fixed capacity and optional coverage."""

    def __init__(self, entries=64, *, hit_latency=1, miss_latency=5, coverage=None):
        self.entries = {}
        self.order = []
        self.entries_max = entries
        self.hit_latency = hit_latency
        self.miss_latency = miss_latency
        self.coverage = coverage
        self.last_latency = 0

    def lookup(self, va, perm='r'):
        vpn = va >> 12
        if vpn in self.entries:
            entry = self.entries[vpn]
            pa = (entry['ppn'] << 12) | (va & 0xFFF)
            fault = perm not in entry['perm']
            hit = True
        else:
            pa = None
            fault = False
            hit = False

        self.last_latency = self.hit_latency if hit else self.miss_latency
        if self.coverage:
            self.coverage.record_tlb('L1', hit)
            self.coverage.record_tlb_latency('L1', self.last_latency)
            if fault:
                self.coverage.record_tlb_fault('L1')

        if hit:
            return True, pa, fault
        return False, None, False

    def refill(self, va, pa, perm='rwx'):
        vpn = va >> 12
        if vpn in self.entries:
            self.order.remove(vpn)
        elif len(self.entries) >= self.entries_max:
            evict = self.order.pop(0)
            del self.entries[evict]
        self.entries[vpn] = {'ppn': pa >> 12, 'perm': perm}
        self.order.append(vpn)
