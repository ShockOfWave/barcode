"""
Tests for AFM analysis functions from the Barcode project.

This module tests the following functions from src/AFM_analize_folder.py:
    - get_acf
    - autocorr_function
    - minmax_db
    - persistance_db

The tests use a dummy CSV file fixture to simulate input data and verify that the
output files (CSV and plots) are created as expected.
"""

import os
import shutil

import pandas as pd
import pytest

from src.AFM_analize_folder import (
    autocorr_function,
    get_acf,
    minmax_db,
    persistance_db,
)


@pytest.fixture
def dummy_csv(tmp_path):
    """
    Create a dummy CSV file for testing.

    The CSV file contains the columns: "DataLine", "Pos = 0", "Pos = 1", and "Pos = 2"
    with sample numeric data.

    Parameters
    ----------
    tmp_path : pathlib.Path
        Temporary directory provided by pytest.

    Returns
    -------
    str
        The file path of the created dummy CSV.
    """
    data = {
        "DataLine": [0, 1, 2],
        "Pos = 0": [1.0, 2.0, 3.0],
        "Pos = 1": [4.0, 5.0, 6.0],
        "Pos = 2": [7.0, 8.0, 9.0],
    }
    df = pd.DataFrame(data)
    file_path = tmp_path / "dummy.csv"
    df.to_csv(file_path, index=False)
    return str(file_path)


def test_get_acf(dummy_csv):
    """
    Test the get_acf function.

    Reads the dummy CSV into a DataFrame, computes the autocorrelation function,
    and asserts that the resulting DataFrame contains the expected columns "ACF" and "ix".
    """
    df = pd.read_csv(dummy_csv)
    acf_df = get_acf(df, nlags=2, series_no=1, constant=1.0, plot_acf=False)
    assert "ACF" in acf_df.columns
    assert "ix" in acf_df.columns


def test_autocorr_function(dummy_csv, tmp_path):
    """
    Test the autocorr_function.

    Copies the dummy CSV to a new file, runs autocorr_function on it, and asserts that
    the output files (an auto CSV and PNG, SVG, PDF plots) are created.
    """
    dest = tmp_path / "dummy_copy.csv"
    shutil.copy(dummy_csv, dest)
    autocorr_function([str(dest)], width_line=1.0)
    # Use [:-4] to remove ".csv" from the filename.
    base = str(dest)[:-4]
    for ext in [
        "_auto.csv",
        "autocorr_function.png",
        "autocorr_function.svg",
        "autocorr_function.pdf",
    ]:
        assert os.path.exists(base + ext)


def test_minmax_db(dummy_csv, tmp_path):
    """
    Test the minmax_db function.

    Copies the dummy CSV to a new file, runs minmax_db on it, and asserts that
    the min/max indices CSV and flattened submatrix CSV are created.
    Cleans up the generated files.
    """
    dest = tmp_path / "dummy_copy.csv"
    shutil.copy(dummy_csv, dest)
    minmax_db([str(dest)])
    base = str(dest)[:-4]
    minmax_file = base + "_min_max_ix(3x3).csv"
    flat_file = base + "_flattened_submat(3x3).csv"
    assert os.path.exists(minmax_file)
    assert os.path.exists(flat_file)
    os.remove(minmax_file)
    os.remove(flat_file)


def test_persistance_db(dummy_csv, tmp_path):
    """
    Test the persistance_db function.

    Copies the dummy CSV to a new file, runs persistance_db on it with a max_edge_length,
    and asserts that the persistence diagram CSV, barcode PNG, and persistence diagram PNG
    are created.
    """
    dest = tmp_path / "dummy_copy.csv"
    shutil.copy(dummy_csv, dest)
    persistance_db([str(dest)], max_edge_length=100)
    base = str(dest)[:-4]
    diag_file = base + "diag_df_output.csv"
    barcode_png = base + "barcode.png"
    persistence_png = base + "persistence_diagram.png"
    assert os.path.exists(diag_file)
    assert os.path.exists(barcode_png)
    assert os.path.exists(persistence_png)
