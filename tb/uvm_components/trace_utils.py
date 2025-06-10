import csv

HEADER = [
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


def save_trace(entries, path):
    """Save *entries* (list of dictionaries) to *path* as CSV."""
    with open(path, "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=HEADER)
        writer.writeheader()
        for e in entries:
            writer.writerow({k: e.get(k) for k in HEADER})


def _parse_value(val):
    if val == "" or val is None:
        return None
    try:
        return int(val)
    except ValueError:
        if val.lower() == "true":
            return True
        if val.lower() == "false":
            return False
        return val


def load_trace(path):
    """Load a reference trace from *path* and return a list of dictionaries."""
    entries = []
    with open(path, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            entry = {k: _parse_value(row.get(k, "")) for k in HEADER}
            entries.append(entry)
    return entries
