"""
Module for preprocessing raw AFM `.txt` files into CSV format.

This module provides a function to recursively locate all `.txt` files
in a source directory, convert them into CSV with appropriate scaling
and column naming, and save them into a structured set of subdirectories.
"""

from pathlib import Path

import pandas as pd
from rich.progress import track


def txt_to_csv_folder(raw_data_path, processed_path, multiply_const=1e9):
    """
    Convert all `.txt` files under a directory into CSV files.

    This function searches `raw_data_path` (recursively) for files with
    the `.txt` extension. Each file is read as a whitespace-delimited
    table (skipping the first four rows), scaled by `multiply_const`,
    and augmented with a `DataLine` column. The positional columns are
    renamed to `"Pos = {i}"`, and the resulting DataFrame is saved as
    `processed_path/{stem}/{stem}.csv`, where `stem` is the original
    filename without extension.

    Parameters
    ----------
    raw_data_path : str or pathlib.Path
        Path to the directory containing raw `.txt` files.
    processed_path : str or pathlib.Path
        Path to the directory where processed CSV files will be placed.
        A subdirectory named after each input file will be created.
    multiply_const : float, default 1e9
        Factor by which to multiply all numeric values after reading.

    Returns
    -------
    None
    """
    raw = Path(raw_data_path)
    proc = Path(processed_path)
    proc.mkdir(parents=True, exist_ok=True)

    txt_files = list(raw.rglob("*.txt"))
    for txt_file in track(txt_files, description="[green]Preprocessing txt->csv..."):
        # Read as whitespace-delimited, skip first 4 lines, no header
        df = (
            pd.read_csv(
                txt_file,
                sep=r"\s+",
                skiprows=4,
                header=None,
                engine="python",
            )
            * multiply_const
        )

        # Insert DataLine index and rename columns
        df.insert(0, "DataLine", range(len(df)))
        df.columns = ["DataLine"] + [f"Pos = {i}" for i in range(df.shape[1] - 1)]

        # Create output directory and save CSV
        stem = txt_file.stem
        out_dir = proc / stem
        out_dir.mkdir(exist_ok=True)
        df.to_csv(out_dir / f"{stem}.csv", index=False)
