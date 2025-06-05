from rtl.smt.smt_arbitration import SmtArb

def test_smt_round_robin():
    arb = SmtArb()
    g0,g1 = arb.cycle(True, True)
    assert g0 != g1
    first = (g0, g1)
    g0,g1 = arb.cycle(True, True)
    assert (g0, g1) != first
