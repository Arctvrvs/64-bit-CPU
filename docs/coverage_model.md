# coverage_model Module

`coverage.py` implements a lightweight functional coverage tracker used by the
Python unit tests. It records which instruction opcodes have executed along with
branch predictor allocations, cache hit/miss statistics, TLB activity and
lookup latency.

## Usage

```python
from tb.uvm_components.coverage import CoverageModel
cov = CoverageModel()
cov.record_opcode(0x33)      # record an R-type instruction
cov.record_btb_event(5, 0x123)
cov.record_cache('L1', True)
cov.record_tlb('L1', False)
cov.record_tlb_latency('L1', 3)
cov.record_tlb_fault('L1')
cov.record_immediate(0x123)
cov.record_page_walk(fault=False)
cov.record_exception('illegal')
cov.record_branch(mispredict=False)
cov.record_vector_load()
cov.record_vector_store()
cov.record_vector_gather()
cov.record_vector_scatter()
report = cov.summary()
print(report['branches'], report['mispredicts'])

cov.reset()  # clear counters between tests
```

`record_immediate()` stores each unique immediate value seen so tests can check
that a variety of immediates were exercised.

`record_exception()` increments a counter for the given fault string so
tests can ensure specific errors are generated.

`summary()` returns a dictionary containing the number of unique opcodes seen,
the count of branch predictor entries, cache hits and misses, TLB hits and
misses, TLB permission faults, recorded TLB lookup latencies, the total number of branch instructions
executed and how many of those were mispredicted, how many unique immediate
values were observed, the number of RSB overflows and underflows, page walk counts
and faults, counts of vector loads and stores, gather/scatter operations,
and a tally of any exceptions recorded. The model
intentionally keeps statistics simple so unit tests can assert coverage results
without a full UVM environment.

Call `reset()` to clear all counters so a single instance can track multiple
test sequences.

``CoverageModel`` can also export its summary directly to JSON using
``save_summary(path)`` and the static ``load_summary(path)`` helper returns
the dictionary from a previously saved file.

Multiple runs can be combined by calling ``merge()`` with another
``CoverageModel`` instance. All counters accumulate and sets of opcodes and
immediates are unified so overall coverage can be reported across test
suites.

The MMU helper classes ``TlbL1`` and ``TlbL2`` accept an optional
``CoverageModel`` instance. When provided, every lookup records hits,
misses, permission faults and the observed latency automatically.
The small cache helpers ``L1DCache``, ``L1ICache``, ``L2Cache`` and
``L3Cache16M8W`` also accept a coverage object and log cache hits or
misses for their respective levels.
The ``BTB`` predictor model likewise accepts a coverage object. Whenever a
new branch target is stored, it records the table index and tag using
``record_btb_event``.
Similarly the ``TAGEPredictor`` records table index and tag pairs via
``record_tage_event`` whenever a new entry is allocated. The indirect
branch predictor logs allocations with ``record_ibp_event``.
The ``ReturnStackBuffer`` records overflow and underflow occurrences
with ``record_rsb_overflow`` and ``record_rsb_underflow`` when given a
coverage object.

The page walker models ``PageWalker`` and ``PageWalker8`` also take an optional
coverage instance. Each translation records a page walk event via
``record_page_walk`` with a flag indicating whether the walk resulted in a
permission fault.
