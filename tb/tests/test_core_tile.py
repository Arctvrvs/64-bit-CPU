from rtl.core_tile_2smts_8wide import CoreTile2SMT8Wide

def test_core_tile_cycles():
    ct = CoreTile2SMT8Wide(core_id=1)
    ct.step()
    ct.step()
    assert ct.cycles == 2
