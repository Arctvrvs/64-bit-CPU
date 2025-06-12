from tb.uvm_components.trace_utils import (
    save_trace,
    load_trace,
    save_trace_json,
    load_trace_json,
)
import os


def test_save_and_load_trace(tmp_path):
    entries = [
        {
            "cycle": 0,
            "pc": 0,
            "instr": 0x13,
            "next_pc": 4,
            "rd_arch": 1,
            "rd_val": 5,
            "store_addr": None,
            "store_data": None,
            "load_addr": None,
            "load_data": None,
            "exception": None,
            "branch_taken": False,
            "branch_target": None,
            "pred_taken": False,
            "pred_target": None,
            "mispredict": False,
            "rob_idx": 0,
        }
    ]
    path = tmp_path / "trace.csv"
    save_trace(entries, path)
    loaded = load_trace(path)
    assert loaded == entries


def test_save_and_load_trace_json(tmp_path):
    entries = [
        {
            "cycle": 1,
            "pc": 4,
            "instr": 0x93,
            "next_pc": 8,
            "rd_arch": 2,
            "rd_val": 10,
            "store_addr": None,
            "store_data": None,
            "load_addr": None,
            "load_data": None,
            "exception": None,
            "branch_taken": False,
            "branch_target": None,
            "pred_taken": False,
            "pred_target": None,
            "mispredict": False,
            "rob_idx": 1,
        }
    ]
    path = tmp_path / "trace.json"
    save_trace_json(entries, path)
    loaded = load_trace_json(path)
    assert loaded == entries
