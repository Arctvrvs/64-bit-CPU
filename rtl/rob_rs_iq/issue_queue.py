class IssueQueue:
    """Simplified issue queue model supporting multiple issues per cycle.

    The model now understands simple functional unit types and a third
    operand used by floating‑point/vector instructions.  Internally
    it keeps separate lists of entries for each type so scheduling can
    respect per‑unit availability.
    """

    FUNC_TYPES = ["int", "fp", "vector", "mem", "branch"]

    CAPACITY = {
        "int": 32,
        "fp": 32,
        "vector": 32,
        "mem": 16,
        "branch": 16,
    }

    def __init__(self, entries=128, issue_width=8):
        self.rs = {t: [] for t in self.FUNC_TYPES}
        self.size = entries
        self.issue_width = issue_width
        self.count = 0

    def flush(self):
        """Clear all queued operations."""
        for t in self.FUNC_TYPES:
            self.rs[t].clear()
        self.count = 0

    def alloc(self, uops):
        """Allocate a list of uops in program order.

        Each uop is a dictionary with keys ``op1``/``op2`` (optional operand
        values if already ready), ``src1_tag``/``src2_tag`` physical register
        indices, ``dest``, ``rob_idx`` and readiness flags ``ready1`` and
        ``ready2``. Invalid uops are skipped.
        Allocation stops when the queue is full.
        """
        for u in uops:
            if self.count >= self.size:
                break
            if not u.get("valid", True):
                continue

            ftype = u.get("func_type", "int")
            if isinstance(ftype, int):
                ftype = self.FUNC_TYPES[ftype]
            if len(self.rs[ftype]) >= self.CAPACITY[ftype]:
                continue

            entry = {
                "op1": u.get("op1"),
                "op2": u.get("op2"),
                "op3": u.get("op3"),
                "pred_mask": u.get("pred_mask", 0),
                "src1_tag": u.get("src1_tag"),
                "src2_tag": u.get("src2_tag"),
                "src3_tag": u.get("src3_tag"),
                "dest": u.get("dest"),
                "rob_idx": u.get("rob_idx"),
                "ready1": u.get("ready1", True),
                "ready2": u.get("ready2", True),
                "ready3": u.get("ready3", True),
                "func_type": ftype,
            }
            self.rs[ftype].append(entry)
            self.count += 1

    def wakeup(self, tag, value):
        """Broadcast a destination tag and value to waiting entries."""
        for lst in self.rs.values():
            for e in lst:
                if not e.get("ready1", True) and e.get("src1_tag") == tag:
                    e["op1"] = value
                    e["ready1"] = True
                if not e.get("ready2", True) and e.get("src2_tag") == tag:
                    e["op2"] = value
                    e["ready2"] = True
                if not e.get("ready3", True) and e.get("src3_tag") == tag:
                    e["op3"] = value
                    e["ready3"] = True

    def issue(self, fu_status=None, max_issue=None):
        """Return up to ``max_issue`` ready uops respecting FU availability."""
        if max_issue is None:
            max_issue = self.issue_width
        if fu_status is None:
            fu_status = {t: max_issue for t in self.FUNC_TYPES}

        avail = {t: fu_status.get(t, 0) for t in self.FUNC_TYPES}

        issued = []
        progress = True
        while len(issued) < max_issue and self.count > 0 and progress:
            progress = False
            for t in self.FUNC_TYPES:
                lst = self.rs[t]
                while lst and avail[t] > 0 and len(issued) < max_issue:
                    e = lst[0]
                    if e.get("ready1", True) and e.get("ready2", True) and e.get("ready3", True):
                        issued.append(lst.pop(0))
                        self.count -= 1
                        avail[t] -= 1
                        progress = True
                    else:
                        break
        return issued
