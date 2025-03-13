"""
Module for converting matrix data from text files to CSV format.

This module provides functions to read matrix data from text files,
process and scale the data, and save the output as CSV files.
"""

import os

import numpy as np
from rich.progress import track


def matrix_convert_save(dataset, save_path):
    """
    Convert matrix data from text files to CSV format and save the results.

    Reads each file provided in the dataset, processes its content by skipping the
    first four lines, converting the remaining data into a numerical matrix scaled by 1e9,
    and prepending row indices along with a header row. Each processed file is saved as a
    CSV file in a subdirectory (named after the file) under the given save_path.

    Parameters
    ----------
    dataset : list of str
        List of file paths containing matrix data in text format.
    save_path : str
        Directory path where the converted CSV files will be saved. A subdirectory
        will be created for each file based on its filename.

    Returns
    -------
    None

    Notes
    -----
    The function performs the following steps for each file in the dataset:
      1. Reads the file and splits each line into a list of string values.
      2. Skips the first four lines (assumed to be non-numerical header information).
      3. Converts the remaining lines to a numerical matrix by:
         - Scaling each numerical value by 10**9.
         - Inserting a row index at the beginning of each row.
      4. Constructs a header row starting with "DataLine" followed by column labels
         ("Pos = 0", "Pos = 1", ...).
      5. Creates the necessary directories if they do not exist.
      6. Saves the final matrix (including the header) as a CSV file using numpy.savetxt.

    A progress bar is displayed during processing using `rich.progress.track`.
    """
    for file in track(dataset, description="[green]Processing..."):
        with open(file) as filik:
            listik = []
            for line in filik:
                stripped_line = line.strip()
                line_list = stripped_line.split()
                listik.append(line_list)
        dfs = listik[4:]
        num_cols = len(dfs[0])
        first_line = ["DataLine"] + [f"Pos = {i}" for i in range(num_cols)]
        dfs_new = [[float(item) * 10**9 for item in row] for row in dfs]
        j = 0
        for j, line in enumerate(dfs_new):
            line.insert(0, j)
        dfs_new.insert(0, first_line)
        file_name = file.split(os.sep)[-1][:-4]
        if not os.path.exists(save_path):
            os.mkdir(save_path)
        file_output_dir = os.path.join(save_path, file_name)
        if not os.path.exists(file_output_dir):
            os.mkdir(file_output_dir)
        np.savetxt(
            os.path.join(file_output_dir, file_name + ".csv"),
            dfs_new,
            fmt="%s",
            delimiter=",",
        )
