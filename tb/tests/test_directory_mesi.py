import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))
from rtl.interconnect.directory_mesi import DirectoryMESI

def test_directory_basic():
    d = DirectoryMESI()
    # core0 read -> state S
    resp = d.access(0x1000, src=0, write=False)
    assert resp['state'] == 'S'
    assert resp['mask'] == 1
    assert not resp['need_inval']
    # core1 read -> still S with both cores
    resp = d.access(0x1000, src=1, write=False)
    assert resp['state'] == 'S'
    assert resp['mask'] == 3
    # core0 write -> need inval of core1
    resp = d.access(0x1000, src=0, write=True)
    assert resp['state'] == 'M'
    assert resp['mask'] == 1
    assert resp['need_inval']
