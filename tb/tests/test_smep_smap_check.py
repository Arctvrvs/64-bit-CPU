from rtl.security.smep_smap_check import SmepSmapCheck


def test_smep_fault():
    chk = SmepSmapCheck()
    assert chk.check(True, True, True, True, False) is True
    assert chk.check(True, False, True, True, False) is False
    assert chk.check(False, True, True, True, False) is False


def test_smap_fault():
    chk = SmepSmapCheck()
    assert chk.check(True, True, False, False, True, False) is True
    assert chk.check(True, True, False, False, True, True) is False
    assert chk.check(True, False, False, False, True, False) is False
