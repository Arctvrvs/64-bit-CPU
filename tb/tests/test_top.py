from tb.uvm_components import Top


def test_top_steps_soc():
    t = Top()
    t.step()
    assert t.cycles == 1
    assert t.soc.cycles == 1
