class Scoreboard:
    """Simple scoreboard using the GoldenModel for reference checking."""

    def __init__(self, start_pc=0, start_rob_idx=0, coverage=None):

    def __init__(self, start_pc=0):

        from rtl.isa.golden_model import GoldenModel
        self.gm = GoldenModel(pc=start_pc)
        self.trace = []
        self.cycle = 0

        self.expected_rob_idx = start_rob_idx
        self.coverage = coverage

    def reset(self, pc=0, rob_idx=0):


    def reset(self, pc=0):

        """Clear state and restart the golden model."""
        from rtl.isa.golden_model import GoldenModel
        self.gm = GoldenModel(pc=pc)
        self.trace.clear()
        self.cycle = 0

        self.expected_rob_idx = rob_idx
        if self.coverage:
            self.coverage.reset()


    def commit(self, instr, rd_arch=None, rd_val=None,
               is_store=False, store_addr=None, store_data=None,
               is_load=False, load_addr=None, load_data=None,
               next_pc=None, exception=None,
               branch_taken=None, branch_target=None,
               pred_taken=None, pred_target=None,
               mispredict=None, rob_idx=None, *, increment_cycle=True):
               mispredict=None, *, increment_cycle=True):

        """Check a committed instruction.

        Parameters
        ----------
        instr : int
            The 32-bit instruction word that retired.
        rd_arch : int or None
            Destination architectural register index (if any).
        rd_val : int or None
            Value written to the destination register by the RTL.
        is_store : bool
            Whether the instruction performed a memory write.
        is_load : bool
            Whether the instruction performed a memory read.
        store_addr : int or None
            Address written on a store.
        store_data : int or None
            Data written on a store.
        load_addr : int or None
            Address read on a load.
        load_data : int or None
            Data returned by the RTL on a load.
        next_pc : int or None
            Program counter after executing ``instr``.
        exception : str or None
            Expected exception code (e.g. ``"illegal"``) or ``None``.
        branch_taken : bool or None
            Actual branch taken flag produced by the RTL.
        branch_target : int or None
            Actual branch target from the RTL when the branch was taken.
        pred_taken : bool or None
            Predictor taken flag used by the RTL.
        pred_target : int or None
            Predictor target used by the RTL.
        mispredict : bool or None
            Branch misprediction indicator from the RTL.
        rob_idx : int or None
            Index of the instruction in the reorder buffer. If provided,
            commit order is verified by expecting consecutive indices.

        Returns
        -------
        bool
            True if the RTL values match the golden model, False otherwise.
        """
        pc_before = self.gm.pc
        opcode = instr & 0x7F
        if self.coverage:
            self.coverage.record_opcode(opcode)
        self.gm.step(instr)
        gm_exc = self.gm.get_last_exception()
        if self.coverage and gm_exc is not None:
            self.coverage.record_exception(gm_exc)
        self.gm.step(instr)
        gm_exc = self.gm.get_last_exception()
        opcode = instr & 0x7F
        branch_instr = opcode in (0x63, 0x6F, 0x67)
        branch_taken_gm = branch_instr and (self.gm.pc != pc_before + 4)
        branch_target_gm = self.gm.pc if branch_taken_gm else None
        current_cycle = self.cycle
        if increment_cycle:
            self.cycle += 1

        ok = True
        if rd_arch is not None:
            if self.gm.regs[rd_arch] != rd_val:
                ok = False
        if is_store and store_addr is not None:
            if self.gm.mem.get(store_addr, 0) != store_data:
                ok = False
        if is_load and load_addr is not None:
            if self.gm.mem.get(load_addr, 0) != load_data:
                ok = False
        if next_pc is not None and self.gm.pc != next_pc:
            ok = False
        if exception is not None and gm_exc != exception:
            ok = False
        if branch_taken is not None and branch_taken != branch_taken_gm:
            ok = False
        if branch_target is not None and branch_target != branch_target_gm:
            ok = False
        calc_misp = False
        if pred_taken is not None:
            calc_misp |= pred_taken != branch_taken_gm
        if branch_taken_gm and pred_target is not None:
            calc_misp |= pred_target != branch_target_gm
        if mispredict is not None:
            if calc_misp != mispredict:
                ok = False
            mispred_flag = mispredict
        else:
            mispred_flag = calc_misp
        if self.coverage and branch_instr:
            self.coverage.record_branch(mispred_flag)
        if rob_idx is not None:
            if rob_idx != self.expected_rob_idx:
                ok = False
            self.expected_rob_idx = (rob_idx + 1) & 0xFFFFFFFF
        if mispredict is not None:
            calc_misp = False
            if pred_taken is not None:
                calc_misp |= pred_taken != branch_taken_gm
            if branch_taken_gm and pred_target is not None:
                calc_misp |= pred_target != branch_target_gm
            if calc_misp != mispredict:
                ok = False
        self.trace.append({
            "cycle": current_cycle,
            "pc": pc_before,
            "instr": instr,
            "next_pc": self.gm.pc,
            "rd_arch": rd_arch,
            "rd_val": self.gm.regs[rd_arch] if rd_arch is not None else None,
            "store_addr": store_addr if is_store else None,
            "store_data": store_data if is_store else None,
            "load_addr": load_addr if is_load else None,
            "load_data": load_data if is_load else None,
            "exception": gm_exc,
            "branch_taken": branch_taken_gm,
            "branch_target": branch_target_gm,
            "pred_taken": pred_taken,
            "pred_target": pred_target,
            "mispredict": mispred_flag,
            "rob_idx": rob_idx,

            "mispredict": mispredict,

        })
        return ok

    def get_trace(self):
        """Return the collected reference trace."""
        return list(self.trace)

    def dump_trace(self, path):
        """Write the trace to *path* in CSV format.

        Parameters
        ----------
        path : str
            Output file path.
        """
        with open(path, "w", encoding="utf-8") as f:
            header = [
                "cycle",
                "pc",
                "instr",
                "next_pc",
                "rd_arch",
                "rd_val",
                "store_addr",
                "store_data",
                "load_addr",
                "load_data",
                "exception",
                "branch_taken",
                "branch_target",
                "pred_taken",
                "pred_target",
                "mispredict",

                "rob_idx",
            ]
            f.write(",".join(header) + "\n")
            for entry in self.trace:
                row = [
                    entry.get("cycle"),
                    entry.get("pc"),
                    entry.get("instr"),
                    entry.get("next_pc"),
                    entry.get("rd_arch"),
                    entry.get("rd_val"),
                    entry.get("store_addr"),
                    entry.get("store_data"),
                    entry.get("load_addr"),
                    entry.get("load_data"),
                    entry.get("exception"),
                    entry.get("branch_taken"),
                    entry.get("branch_target"),
                    entry.get("pred_taken"),
                    entry.get("pred_target"),
                    entry.get("mispredict"),
                    entry.get("rob_idx"),
                ]
                f.write(",".join("" if v is None else str(v) for v in row) + "\n")

    def commit_bundle(self, instrs, rd_arch_list=None, rd_val_list=None,
                      is_store_list=None, store_addr_list=None,
                      store_data_list=None, is_load_list=None,
                      load_addr_list=None, load_data_list=None,
                      next_pc_list=None, exception_list=None,
                      branch_taken_list=None, branch_target_list=None,
                      pred_taken_list=None, pred_target_list=None,
                      mispredict_list=None, rob_idx_list=None):
                      mispredict_list=None):
        """Commit a bundle of instructions retiring in the same cycle.

        Parameters
        ----------
        instrs : list[int]
            Instruction words to retire (up to 8).
        rd_arch_list, rd_val_list, is_store_list, store_addr_list,
        store_data_list, is_load_list, load_addr_list, load_data_list,
        next_pc_list, exception_list,
        branch_taken_list, branch_target_list,
        pred_taken_list, pred_target_list,
        mispredict_list : list or None
            Per-instruction parameters analogous to :py:meth:`commit`.
        rob_idx_list : list or None
            ROB indices used to verify commit order.

        Returns
        -------
        list[bool]
            Result of reference checks for each instruction.
        """
        n = len(instrs)
        rd_arch_list = rd_arch_list or [None] * n
        rd_val_list = rd_val_list or [None] * n
        is_store_list = is_store_list or [False] * n
        store_addr_list = store_addr_list or [None] * n
        store_data_list = store_data_list or [None] * n
        is_load_list = is_load_list or [False] * n
        load_addr_list = load_addr_list or [None] * n
        load_data_list = load_data_list or [None] * n
        next_pc_list = next_pc_list or [None] * n
        exception_list = exception_list or [None] * n
        branch_taken_list = branch_taken_list or [None] * n
        branch_target_list = branch_target_list or [None] * n
        pred_taken_list = pred_taken_list or [None] * n
        pred_target_list = pred_target_list or [None] * n
        mispredict_list = mispredict_list or [None] * n
        rob_idx_list = rob_idx_list or [None] * n

        current_cycle = self.cycle
        results = []
        for i in range(n):
            ok = self.commit(
                instrs[i],
                rd_arch=rd_arch_list[i],
                rd_val=rd_val_list[i],
                is_store=is_store_list[i],
                store_addr=store_addr_list[i],
                store_data=store_data_list[i],
                is_load=is_load_list[i],
                load_addr=load_addr_list[i],
                load_data=load_data_list[i],
                next_pc=next_pc_list[i],
                exception=exception_list[i],
                branch_taken=branch_taken_list[i],
                branch_target=branch_target_list[i],
                pred_taken=pred_taken_list[i],
                pred_target=pred_target_list[i],
                mispredict=mispredict_list[i],
                rob_idx=rob_idx_list[i],
                increment_cycle=False,
            )
            # fix up the cycle for this trace entry to match the bundle cycle
            self.trace[-1]["cycle"] = current_cycle
            results.append(ok)

        self.cycle += 1
        return results
