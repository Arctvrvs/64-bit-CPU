# coverage_model Module

`coverage.py` implements a lightweight functional coverage tracker used by the
Python unit tests. It records which instruction opcodes have executed along with
branch predictor allocations, cache hit/miss statistics and TLB activity.

## Usage

```python
from tb.uvm_components.coverage import CoverageModel
cov = CoverageModel()
cov.record_opcode(0x33)      # record an R-type instruction
cov.record_btb_event(5, 0x123)
cov.record_cache('L1', True)
cov.record_tlb('L1', False)
cov.record_exception('illegal')
cov.record_branch(mispredict=False)
report = cov.summary()
print(report['branches'], report['mispredicts'])

cov.reset()  # clear counters between tests
```

`record_exception()` increments a counter for the given fault string so
tests can ensure specific errors are generated.

`summary()` returns a dictionary containing the number of unique opcodes seen,
the count of branch predictor entries, cache hits and misses, TLB hits and
misses, the total number of branch instructions executed and how many of those
were mispredicted, and a tally of any exceptions recorded. The model
intentionally keeps statistics simple so unit tests can assert coverage results
without a full UVM environment.

Call `reset()` to clear all counters so a single instance can track multiple
test sequences.
