# scoreboard Module

`scoreboard.py` implements a very small reference checker used by the
Python unit tests.  It relies on the `GoldenModel` interpreter to validate
results from the pipeline.

The checker supports integer, floating-point and vector instructions,
including 32-bit `ADDW`/`SUBW` and shift forms in addition to full 64-bit
arithmetic. Floating-point operations cover add, subtract, multiply,
divide, min/max and the
fused multiply-add/subtract instructions (`FMADD.D`, `FMSUB.D`, `FNMSUB.D`,
`FNMADD.D`). Vector instructions cover
add, multiply and fused multiply-add operations, so unit tests can cover the
full execution pipeline.

The class exposes a `commit()` method which is called for every instruction
that retires from the reorder buffer.  The scoreboard feeds the instruction to
the golden model and compares the destination register, any store or load data, and
(optionally) the next program counter and exception code.  Each commit is recorded so a reference
trace can be retrieved later.  The trace includes the retire **cycle** number
starting from zero.  When ``rob_idx`` values are provided the scoreboard
verifies that instructions retire sequentially.

When SEV style memory encryption is active in the golden model the scoreboard
decrypts memory contents automatically when verifying loads and stores so tests
do not need to adjust expected data for the key in use.
If Meltdown protection is disabled in the golden model the scoreboard will
still compare the leaked register value even when a permission fault occurs.
When virtualization is enabled through the ``VMCS`` the checker also
translates guest physical addresses with the ``EPT`` stub so ``load_addr`` and
``store_addr`` parameters should refer to the resulting host address.


## Usage

```python
from tb.uvm_components.scoreboard import Scoreboard
from tb.uvm_components.coverage import CoverageModel

cov = CoverageModel()
sb = Scoreboard(start_pc=0, coverage=cov)
passed = sb.commit(instr, rd_arch=5, rd_val=42, next_pc=4)
passed_exc = sb.commit(0xffffffff, exception="illegal")
load_ok = sb.commit(
    instr_load,
    rd_arch=1,
    rd_val=0x55,
    is_load=True,
    load_addr=0x100,
    load_data=0x55,
)
pf = sb.commit(some_load, exception="page")
```


When a ``CoverageModel`` is supplied the scoreboard automatically records
executed opcodes, immediate values, branch outcomes and any exceptions (including
``nx``, ``smep``, ``smap``, ``ecall``, ``ebreak`` and ``sgx`` faults) into the coverage tracker. Vector loads,
stores and gather/scatter operations also update dedicated counters in the
coverage model.
TLB lookups performed by the golden model are logged as hits or misses and
page walks are counted as well when a coverage instance is provided.


The method returns `True` when the provided values match the reference
model, otherwise `False`.

`FENCE` and `FENCE.I` instructions are treated as no-ops by the checker and
simply advance the program counter. The speculative fetch fence
`SPEC_FENCE` likewise advances the PC but causes subsequent loads to be
checked for a `"spec"` exception until a branch instruction retires.

`next_pc` can be omitted if checking of the program counter is not

needed.  Provide an ``exception`` string (for example ``"illegal``",
 ``"misalign"``, ``"page"``, ``"nx"``, ``"smep"``, ``"smap"``, ``"ecall```, ``"ebreak`` or ``"sgx"``) to verify that the golden model reports the same fault
as the RTL.  Specify ``is_load=True`` together with ``load_addr`` and
``load_data`` to verify the value returned by a load instruction against the
model's memory.  Set ``is_store=True`` and provide ``store_addr`` and
``store_data`` to check that memory writes hit the expected location.  Passing
``exception="page"`` allows tests to check page faults triggered by the golden
model.


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

Use `dump_trace(path)` to write the collected trace to a CSV file.  The
method delegates to `trace_utils.save_trace()` so the file is compatible
with `trace_utils.load_trace()` for round‑trip testing. Use
`dump_trace_json(path)` for a JSON representation powered by
`trace_utils.save_trace_json()`.  Both helpers return the list produced by
`get_trace()`:

```python
sb.commit(0x00500093, rd_arch=1, rd_val=5)
trace = sb.dump_trace("trace.csv")
print(len(trace))
sb.dump_trace_json("trace.json")
```

The CSV contains a ``rob_idx`` column when commit ordering is checked.

If a ``CoverageModel`` was supplied, call `dump_coverage(path)` to
write the coverage summary to a JSON file. The method also returns the
summary dictionary for convenience:

```python
summary = sb.dump_coverage("coverage.json")
```

Use `get_coverage_summary()` to obtain the same dictionary without writing a
file:

```python
summary = sb.get_coverage_summary()
print(summary)
```

When the scoreboard was created without a ``CoverageModel`` this helper
returns an empty dictionary.

Use `reset()` to clear the trace and restart the golden model if a test needs
to run multiple sequences from a fresh PC.  When a coverage model is attached,
the counters are cleared as well so each run starts with fresh statistics.

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

## Vector Gather/Scatter Helpers

Vector load/store operations that use per-lane indices can be checked with
``check_gather`` and ``check_scatter``.  These helpers call the matching methods
in the :class:`GoldenModel` and compare the observed data to the model.

```python
idx = [7, 0, 3, 1, 4, 6, 2, 5]
vec = sb.gm.gather(base, idx, 3)
passed = sb.check_gather(base, idx, 3, vec)
passed_store = sb.check_scatter(base + 0x40, idx, 3, vec)
```

Both methods return ``True`` when the golden model reports no exception and the
values match the reference memory contents. Successful checks increment the
``vector_gathers`` and ``vector_scatters`` counters respectively when a
``CoverageModel`` is attached.
