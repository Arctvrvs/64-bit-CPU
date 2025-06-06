# scoreboard Module

`scoreboard.py` implements a tiny scoreboard used by the Python unit tests.
It collects expected values and compares them against actual observations.

## Usage

```
from tb.uvm_components import Scoreboard
sb = Scoreboard()
sb.add_expected(42)
sb.add_actual(42)
assert sb.check()
```

The implementation is deliberately simple so future UVM components can
leverage it when verifying the RTL blocks in this repository.
