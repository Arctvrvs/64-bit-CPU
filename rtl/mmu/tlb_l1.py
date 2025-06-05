class TlbL1:
    """Simple L1 TLB model with fixed capacity."""
    def __init__(self, entries=64):
        self.entries = {}
        self.order = []
        self.entries_max = entries

    def lookup(self, va, perm='r'):
        vpn = va >> 12
        if vpn in self.entries:
            entry = self.entries[vpn]
            pa = (entry['ppn'] << 12) | (va & 0xFFF)
            fault = perm not in entry['perm']
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
