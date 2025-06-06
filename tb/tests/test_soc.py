from rtl.riscv_soc_4core import RiscvSoC4Core


def test_soc_steps_all_cores():
    soc = RiscvSoC4Core()
    soc.step()
    assert soc.cycles == 1
    for c in soc.cores:
        assert c.cycles == 1
