class BranchPredictorTop:
    """Simplified top level branch predictor used in unit tests."""

    def __init__(self, entries=32, *, coverage=None):
        from .btb import BTB
        from .tage import TAGEPredictor
        from .ibp import IBPPredictor
        from .rsb32 import ReturnStackBuffer
        self.coverage = coverage
        self.btb = BTB(entries=entries, coverage=coverage)
        self.tage = TAGEPredictor(coverage=coverage)
        self.ibp = IBPPredictor(coverage=coverage)
        self.rsb = ReturnStackBuffer(coverage=coverage)
        self.last_target = 0

    def predict(self, pc, is_call=False, is_ret=False,
                is_cond_branch=False, is_uncond_branch=False,
                is_indirect=False, last_target=None):
        """Return (taken, predicted_pc) for the given instruction."""
        if is_ret:
            return True, self.rsb.top()

        if is_uncond_branch:
            # Use BTB target; unconditional branches are always taken
            _, target = self.btb.predict(pc)
            if is_call:
                self.rsb.push((pc + 4) & 0xFFFFFFFFFFFFFFFF)
            return True, target

        if is_cond_branch:
            taken = self.tage.predict(pc)
            if taken:
                _, target = self.btb.predict(pc)
                return True, target
            return False, (pc + 4) & 0xFFFFFFFFFFFFFFFF

        if is_indirect:
            tgt = self.ibp.predict(pc, self.last_target if last_target is None else last_target)
            return True, tgt

        return False, (pc + 4) & 0xFFFFFFFFFFFFFFFF

    def update(self, pc, actual_taken, actual_target,
               is_branch=False, is_indirect=False, is_ret=False):
        """Update predictor state with actual branch outcome."""
        if is_branch:
            self.btb.update(pc, actual_target, actual_taken)
            self.tage.update(pc, actual_taken)
        if is_indirect:
            self.ibp.update(pc, self.last_target, actual_target)
        if is_ret:
            self.rsb.pop()
        self.last_target = actual_target & 0xFFFFFFFFFFFFFFFF
