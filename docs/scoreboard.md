# scoreboard Module

`scoreboard.py` implements a very small reference checker used by the
Python unit tests.  It relies on the `GoldenModel` interpreter to validate
results from the pipeline.

The class exposes a `commit()` method which is called for every instruction
that retires from the reorder buffer.  The scoreboard feeds the instruction to
the golden model and compares the destination register, any store or load data, and
(optionally) the next program counter and exception code.  Each commit is recorded so a reference
trace can be retrieved later.  The trace includes the retire **cycle** number
starting from zero.  When ``rob_idx`` values are provided the scoreboard
verifies that instructions retire sequentially.

## Usage

```python
from tb.uvm_components.scoreboard import Scoreboard
from tb.uvm_components.coverage import CoverageModel

cov = CoverageModel()
sb = Scoreboard(start_pc=0, coverage=cov)
passed = sb.commit(instr, rd_arch=5, rd_val=42, next_pc=4)
passed_exc = sb.commit(0xffffffff, exception="illegal")
pf = sb.commit(some_load, exception="page")
load_ok = sb.commit(instr_load, rd_arch=1, rd_val=0x55,
                    is_load=True, load_addr=0x100, load_data=0x55)
```

When a ``CoverageModel`` is supplied the scoreboard automatically records
executed opcodes, branch outcomes and any exceptions into the coverage tracker.

The method returns `True` when the provided values match the reference
model, otherwise `False`.

`next_pc` can be omitted if checking of the program counter is not
needed.  Provide an ``exception`` string (for example ``"illegal"``,
``"misalign"`` or ``"page"``) to verify that the golden model reports the same fault
as the RTL.
Specify ``is_load=True`` together with ``load_addr`` and ``load_data`` to
verify the value returned by a load instruction against the model's
memory. Set ``is_store=True`` and provide ``store_addr`` and
``store_data`` to check that memory writes hit the expected location.
Passing ``exception="page"`` allows tests to check page faults triggered
by the golden model.

Branches may also be checked by passing ``branch_taken`` and
``branch_target``.  When prediction information is provided via
``pred_taken`` and ``pred_target`` the ``mispredict`` flag is verified as
well.

To verify commit ordering you may provide a ``rob_idx`` number with each
call to ``commit``.  The scoreboard will expect these indices to increase
sequentially:

```python
sb.commit(instr0, rd_arch=1, rd_val=5, rob_idx=0)
sb.commit(instr1, rd_arch=2, rd_val=3, rob_idx=1)
```

The scoreboard accumulates a simple trace.  Call `get_trace()` to obtain a
list of commit dictionaries for post-processing.  Each dictionary contains
`cycle`, `pc`, `next_pc`, `rd_arch`, `rd_val`, optional store or load
information, and any `exception` string.

Use `dump_trace(path)` to write the collected trace to a CSV file that
can be compared with other reference traces or inspected manually.

```python
sb.commit(0x00500093, rd_arch=1, rd_val=5)
sb.dump_trace("trace.csv")
```
The CSV contains a ``rob_idx`` column when commit ordering is checked.

Use `reset()` to clear the trace and restart the golden model if a test needs
to run multiple sequences from a fresh PC.

To retire multiple instructions in the same cycle use `commit_bundle()`:

```python
results = sb.commit_bundle(
    [instr0, instr1],
    rd_arch_list=[1, 2],
    rd_val_list=[5, 3],
    is_store_list=[False, True],
    store_addr_list=[None, 0x200],
    store_data_list=[None, 0xDEADBEEF],
    is_load_list=[True, False],
    load_addr_list=[0x100, None],
    load_data_list=[0x55, None],
    next_pc_list=[4, 8],
    exception_list=[None, None],
    branch_taken_list=[False, True],
    branch_target_list=[None, 0x10],
    pred_taken_list=[False, True],
    pred_target_list=[None, 0x10],
    mispredict_list=[False, False],
    rob_idx_list=[0, 1],
)
```

`commit_bundle` returns a list of boolean results while recording each
instruction with the same cycle number.

For tests that directly observe the architectural register file write
ports, a small helper `regfile_bfm` is provided. It uses the same
`GoldenModel` to verify individual register writes without tracking
program counter or memory state.
