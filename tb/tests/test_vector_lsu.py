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
