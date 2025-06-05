from rtl.security.nx_check import NXCheck


def test_nx_basic():
    nx = NXCheck()
    assert nx.check(True, False) is False
    assert nx.check(True, True) is True
    assert nx.check(False, True) is False
