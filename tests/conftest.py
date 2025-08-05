import os
import shutil
import tempfile
import numpy as np
import pytest


@pytest.fixture
def temp_data_dir():
    """Provide temporary directory with sample AFM txt files."""
    temp_dir = tempfile.mkdtemp()
    try:
        for i in range(3):
            data = np.random.rand(8, 8) * 1e-7
            file_path = os.path.join(temp_dir, f"test_data_{i}.txt")
            with open(file_path, "w") as f:
                f.write("# Канал: Height (2)\n")
                f.write("# Ширина: 5.02 µm\n")
                f.write("# Высота: 5.02 µm\n")
                f.write("# Единицы измерения: m\n")
                for row in data:
                    f.write("\t".join(f"{val:.6e}" for val in row) + "\n")
        yield temp_dir
    finally:
        shutil.rmtree(temp_dir)
