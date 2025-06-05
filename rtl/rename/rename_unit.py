class RenameUnit:
    """Simple rename unit model with a free list and mapping table."""
    def __init__(self, phys_regs=128, arch_regs=32):
        self.phys_regs = phys_regs
        self.arch_regs = arch_regs
        self.mapping = list(range(arch_regs))
        self.free_list = list(range(arch_regs, phys_regs))

    def free_count(self):
        return len(self.free_list)

    def allocate(self, insts):
        """Rename a list of instructions.
        Each instruction is a dict with keys: 'valid', 'rs1', 'rs2', 'rd'.
        Returns a list of dicts with physical register mappings and old mapping."""
        results = []
        for inst in insts:
            if not inst.get('valid', True):
                results.append({'valid': False})
                continue
            rd = inst.get('rd', 0)
            if self.free_count() == 0:
                results.append({'valid': False})
                continue
            old = self.mapping[rd]
            phys = self.free_list.pop(0) if rd != 0 else 0
            if rd != 0:
                self.mapping[rd] = phys
            res = {
                'rs1_phys': self.mapping[inst.get('rs1', 0)],
                'rs2_phys': self.mapping[inst.get('rs2', 0)],
                'rd_phys': phys,
                'old_phys': old,
                'valid': True,
            }
            results.append(res)
        return results

    def free(self, phys_idx):
        if phys_idx >= self.arch_regs and phys_idx not in self.free_list:
            self.free_list.append(phys_idx)
