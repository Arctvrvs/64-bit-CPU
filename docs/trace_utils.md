# trace_utils Module

`trace_utils.py` provides small helpers for dealing with reference traces.
The functions mirror the CSV layout produced by `Scoreboard.dump_trace()`.

```python
from tb.uvm_components import save_trace, load_trace

data = [{"cycle": 0, "pc": 0, "instr": 0x13}]
save_trace(data, "trace.csv")
restored = load_trace("trace.csv")
```

`save_trace()` writes the list of dictionaries using the standard CSV header,
while `load_trace()` parses that file back into Python dictionaries with
integers and booleans converted from strings.

The ``tb.uvm_components`` package re-exports these helpers so they can be
imported directly:

```python
from tb.uvm_components import save_trace, load_trace
```
