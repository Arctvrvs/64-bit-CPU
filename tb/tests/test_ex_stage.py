import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from rtl.ex_stage.ex_stage import ExStage

def test_ex_stage_basic():
    ex = ExStage()
    issues = [None]*8
    issues[0] = {'fu':0,'op1':1,'op2':2,'op3':0,'dest':5,'rob':1}
    wb = ex.cycle(issues)
    assert all(x is None for x in wb)
    wb = ex.cycle([None]*8)
    assert wb[0]['result'] == 3
    assert wb[0]['dest'] == 5
    assert wb[0]['rob'] == 1

def test_ex_stage_vector_fma():
    ex = ExStage()
    issues = [None]*8
    issues[0] = {'fu':2,'op1':2,'op2':3,'op3':4,'dest':6,'rob':2}
    wb = ex.cycle(issues)
    for _ in range(4):
        wb = ex.cycle([None]*8)
        assert all(x is None for x in wb)
    wb = ex.cycle([None]*8)
    assert wb[3]['result'] == 2*3+4
    assert wb[3]['dest'] == 6
    assert wb[3]['rob'] == 2

def test_ex_stage_flush():
    ex = ExStage()
    issues = [None]*8
    issues[0] = {'fu':0,'op1':1,'op2':2,'dest':1,'rob':0}
    ex.cycle(issues)
    wb = ex.cycle([None]*8, flush=True)
    assert all(x is None for x in wb)
    wb = ex.cycle([None]*8)
    assert all(x is None for x in wb)

def test_ex_stage_branch_mispredict():
    ex = ExStage()
    issues = [None]*8
    issues[0] = {
        'fu': 4,
        'op1': 1,
        'op2': 1,
        'op3': 8,
        'pc': 0,
        'branch_ctrl': 0,
        'pred_taken': False,
        'pred_target': 4,
        'dest': 0,
        'rob': 3,
    }
    wb = ex.cycle(issues)
    wb = ex.cycle([None]*8)
    assert wb[7]['mispredict']
    assert wb[7]['target'] == 8

def test_ex_stage_branch_correct():
    ex = ExStage()
    issues = [None]*8
    issues[0] = {
        'fu': 4,
        'op1': 1,
        'op2': 1,
        'op3': 8,
        'pc': 0,
        'branch_ctrl': 0,
        'pred_taken': True,
        'pred_target': 8,
        'dest': 0,
        'rob': 4,
    }
    ex.cycle(issues)
    wb = ex.cycle([None]*8)
    assert not wb[7]['mispredict']
    assert wb[7]['target'] == 8

def test_ex_stage_fu_status():
    ex = ExStage()
    assert ex.fu_status()['int'] == 2
    issues = [None]*8
    issues[0] = {'fu':0,'op1':1,'op2':1,'dest':1,'rob':0}
    ex.cycle(issues)
    assert ex.fu_status()['int'] == 1
    ex.cycle([None]*8)
    ex.cycle([None]*8)
    assert ex.fu_status()['int'] == 2
