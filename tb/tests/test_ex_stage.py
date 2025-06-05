from rtl.ex_stage.ex_stage import ExStage

def test_ex_stage_basic():
    ex = ExStage()
    issues = [None]*8
    issues[0] = {'fu':0,'op1':1,'op2':2,'dest':5,'rob':1}
    wb = ex.cycle(issues)
    assert all(x is None for x in wb)
    wb = ex.cycle([None]*8)
    assert wb[0]['data'] == 3
    assert wb[0]['dest'] == 5
    assert wb[0]['rob'] == 1
