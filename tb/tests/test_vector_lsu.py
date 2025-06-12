import os
import sys
import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))
from rtl.lsu.vector_lsu import VectorLSU


def test_vector_lsu_load_store():
    vlsu = VectorLSU()
    base = 0x1000
    data = int.from_bytes(bytes(range(8)), 'little')
    vlsu.store(base, data)
    assert vlsu.load(base) == data


def test_vector_lsu_gather_scatter():
    vlsu = VectorLSU()
    base = 0x2000
    idx = [7, 6, 5, 4, 3, 2, 1, 0]
    data = int.from_bytes(bytes(range(10, 18)), "little")
    vlsu.scatter(base, idx, 3, data)
    assert vlsu.gather(base, idx, 3) == data
