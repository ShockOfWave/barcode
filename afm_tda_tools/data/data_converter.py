"""
Utilities for preprocessing raw AFM `.txt` files into CSV format.

The original project defined a single function :func:`txt_to_csv_folder`
which locates all text files in a directory, converts them to CSV,
scales the numeric values, adds a ``DataLine`` column, and saves the
result to a separate subdirectory for each file.  This function is
preserved here but moved into a dedicated ``data`` subpackage to
emphasise its role as a preprocessing step rather than part of the
analysis pipeline.
"""

from __future__ import annotations

from pathlib import Path
from typing import Iterable

import pandas as pd
from rich.progress import track


def txt_to_csv_folder(raw_data_path: str | Path, processed_path: str | Path, multiply_const: float = 1e9) -> None:
    """
    Convert all `.txt` files under a directory into CSV files.

    This function searches ``raw_data_path`` recursively for files with the
    `.txt` extension.  Each file is read as a whitespace‑delimited table
    (skipping the first four rows), scaled by ``multiply_const``, and
    augmented with a ``DataLine`` column.  The positional columns are
    renamed to ``"Pos = {i}"``, and the resulting DataFrame is saved
    under ``processed_path/{stem}/{stem}.csv``, where ``stem`` is the
    original filename without extension.

    Parameters
    ----------
    raw_data_path : str or pathlib.Path
        Path to the directory containing raw `.txt` files.
    processed_path : str or pathlib.Path
        Path to the directory where processed CSV files will be placed.
        A subdirectory named after each input file will be created.
    multiply_const : float, optional
        Factor by which to multiply all numeric values after reading.
        Default is ``1e9`` to convert units.
    """
    raw = Path(raw_data_path)
    proc = Path(processed_path)
    proc.mkdir(parents=True, exist_ok=True)

    txt_files: Iterable[Path] = raw.rglob("*.txt")
    for txt_file in track(list(txt_files), description="[green]Preprocessing txt->csv..."):
        # Read as whitespace‑delimited, skip first 4 lines, no header
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