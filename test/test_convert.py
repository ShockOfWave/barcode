"""
Tests for the convert module.

This module tests the matrix_convert_save function from src.convert.
It creates a dummy text file with header lines and matrix data, converts it
to CSV using matrix_convert_save, and verifies that the output CSV file is
created and contains the expected content.
"""

import os

import pandas as pd

from src.convert import matrix_convert_save


def test_matrix_convert_save(tmp_path):
    """
    Test the matrix_convert_save function.

    Creates a temporary text file with 4 header lines followed by matrix data
    (2 data rows). The function matrix_convert_save is then invoked to convert the
    text file to a CSV file. The test asserts that the expected output directory and
    CSV file are created, and that the CSV contains the "DataLine" column.

    Parameters
    ----------
    tmp_path : pathlib.Path
        Temporary directory provided by pytest for test file creation.

    Returns
    -------
    None
    """
    # Create a dummy text file with header lines and matrix data.
    content = "header1\nheader2\nheader3\nheader4\n1.0 2.0 3.0\n4.0 5.0 6.0\n"
    txt_file = tmp_path / "test.txt"
    txt_file.write_text(content)
    dataset = [str(txt_file)]
    save_path = str(tmp_path / "output")

    # Run the conversion function.
    matrix_convert_save(dataset, save_path)

    # Expect that a directory named "test" is created inside the output directory,
    # and that it contains a file named "test.csv".
    output_csv = os.path.join(save_path, "test", "test.csv")
    assert os.path.exists(output_csv)

    # Minimal check of CSV content: it should contain the "DataLine" column.
    df = pd.read_csv(output_csv)
    assert "DataLine" in df.columns
