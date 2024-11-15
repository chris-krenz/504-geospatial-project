"""
TODO: Develop more...
"""

import pytest
import numpy as np
from lsh import MultiTableLSH
from data_importer import DataPoint


data_points = [
    DataPoint(latitude=18.34, longitude=-64.92, zip_code="00802"),
    DataPoint(latitude=18.35, longitude=-64.93, zip_code="00803"),
    DataPoint(latitude=18.30, longitude=-64.90, zip_code="00804"),
    DataPoint(latitude=18.29, longitude=-64.89, zip_code="00805"),
]


@pytest.fixture
def lsh():
    lsh = MultiTableLSH(num_tables=3, hash_size=2)
    lsh.insert(data_points)
    return lsh

def test_initialization(lsh):
    assert len(lsh.hash_tables) == 3, "Should init w/ 3 hash tables"
    assert len(lsh.projections) == 3, "Should init w/ 3 proj tables"
