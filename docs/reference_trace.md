# Reference Trace Format

The scoreboard collects a cycle by cycle trace of retired instructions. Each
entry contains the program counter, writeback information and optional load or
store details. The trace can be exported to CSV or loaded back for analysis.

The CSV header is:

```
cycle,pc,instr,next_pc,rd_arch,rd_val,store_addr,store_data,load_addr,load_data,exception,branch_taken,branch_target,pred_taken,pred_target,mispredict,rob_idx
```

Use `dump_trace()` from `scoreboard.py` to write a trace:

```python
from tb.uvm_components.scoreboard import Scoreboard
sb = Scoreboard()
...
sb.dump_trace("trace.csv")  # internally calls ``trace_utils.save_trace``
```

The companion helpers in `trace_utils.py` can parse the CSV back into a list of
dictionaries:

```python
from tb.uvm_components.trace_utils import load_trace
entries = load_trace("trace.csv")
```

`save_trace()` performs the inverse operation and is useful when constructing
expected traces for comparison in unit tests.
