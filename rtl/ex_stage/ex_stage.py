from rtl.ex_units.branch_unit import BranchUnit


class ExStage:
    """Python model of ``ex_stage.sv`` with simple per-unit pipelines."""

    def __init__(self):
        self.branch = BranchUnit()
        self.int_slots = [None, None]
        self.mul_slot = None
        self.vec_slots = [None, None]
        self.mem_slots = [None, None]
        self.branch_slot = None

    def flush(self):
        self.int_slots = [None, None]
        self.mul_slot = None
        self.vec_slots = [None, None]
        self.mem_slots = [None, None]
        self.branch_slot = None

    def fu_status(self):
        return {
            "int": 2 - sum(1 for s in self.int_slots if s is not None),
            "mul": 0 if self.mul_slot else 1,
            "vector": 2 - sum(1 for s in self.vec_slots if s is not None),
            "mem": 2 - sum(1 for s in self.mem_slots if s is not None),
            "branch": 0 if self.branch_slot else 1,
        }

    def _advance(self, slot):
        if slot is not None:
            slot["count"] -= 1
            if slot["count"] <= 0:
                return True
        return False

    def cycle(self, issues, flush=False):
        if flush:
            self.flush()
            return [None] * 8
        wb = [None] * 8
        # advance
        for i, s in enumerate(self.int_slots):
            if self._advance(s):
                wb[i] = {
                    "result": s["data"],
                    "dest": s["dest"],
                    "rob": s["rob"],
                    "mispredict": False,
                    "target": 0,
                }
                self.int_slots[i] = None
        if self._advance(self.mul_slot):
            wb[2] = {
                "result": self.mul_slot["data"],
                "dest": self.mul_slot["dest"],
                "rob": self.mul_slot["rob"],
                "mispredict": False,
                "target": 0,
            }
            self.mul_slot = None
        for i, s in enumerate(self.vec_slots):
            idx = 3 + i
            if self._advance(s):
                wb[idx] = {
                    "result": s["data"],
                    "dest": s["dest"],
                    "rob": s["rob"],
                    "mispredict": False,
                    "target": 0,
                }
                self.vec_slots[i] = None
        for i, s in enumerate(self.mem_slots):
            idx = 5 + i
            if self._advance(s):
                wb[idx] = {
                    "result": s["data"],
                    "dest": s["dest"],
                    "rob": s["rob"],
                    "mispredict": False,
                    "target": 0,
                }
                self.mem_slots[i] = None
        if self._advance(self.branch_slot):
            wb[7] = {
                "result": 0,
                "dest": self.branch_slot["dest"],
                "rob": self.branch_slot["rob"],
                "mispredict": self.branch_slot["mispredict"],
                "target": self.branch_slot["target"],
            }
            self.branch_slot = None

        # accept new issues
        for issue in issues:
            if issue is None:
                continue
            fu = issue.get("fu", 0)
            dest = issue.get("dest")
            rob = issue.get("rob")
            op1 = issue.get("op1", 0)
            op2 = issue.get("op2", 0)
            op3 = issue.get("op3", 0)
            if fu == 0:
                for i in range(2):
                    if self.int_slots[i] is None:
                        self.int_slots[i] = {
                            "data": (op1 + op2) & 0xFFFFFFFFFFFFFFFF,
                            "dest": dest,
                            "rob": rob,
                            "count": 1,
                        }
                        break
            elif fu == 1:
                if self.mul_slot is None:
                    self.mul_slot = {
                        "data": (op1 * op2) & 0xFFFFFFFFFFFFFFFF,
                        "dest": dest,
                        "rob": rob,
                        "count": 3,
                    }
            elif fu == 2:
                for i in range(2):
                    if self.vec_slots[i] is None:
                        self.vec_slots[i] = {
                            "data": ((op1 * op2 + op3) & 0xFFFFFFFFFFFFFFFF),
                            "dest": dest,
                            "rob": rob,
                            "count": 5,
                        }
                        break
            elif fu == 3:
                for i in range(2):
                    if self.mem_slots[i] is None:
                        self.mem_slots[i] = {
                            "data": op2 & 0xFFFFFFFFFFFFFFFF,
                            "dest": dest,
                            "rob": rob,
                            "count": 2,
                        }
                        break
            else:
                if self.branch_slot is None:
                    res = self.branch.compute(
                        issue.get("branch_ctrl", BranchUnit.BEQ),
                        op1,
                        op2,
                        issue.get("pc", 0),
                        op3,
                        issue.get("pred_taken", False),
                        issue.get("pred_target", 0),
                    )
                    self.branch_slot = {
                        "mispredict": res["mispredict"],
                        "target": res["target"],
                        "dest": dest,
                        "rob": rob,
                        "count": 1,
                    }
        return wb
