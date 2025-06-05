class DirectoryMESI:
    """Tiny MESI directory model."""
    def __init__(self):
        self.entries = {}

    def access(self, addr, src, write=False):
        state, mask = self.entries.get(addr, ('I', 0))
        need_inval = False
        if write:
            need_inval = mask & ~(1 << src) != 0 and state != 'I'
            state = 'M'
            mask = 1 << src
        else:
            if state == 'I':
                state = 'S'
                mask = 1 << src
            else:
                mask |= 1 << src
                state = 'S'
        self.entries[addr] = (state, mask)
        return {'state': state, 'need_inval': need_inval, 'mask': mask}
