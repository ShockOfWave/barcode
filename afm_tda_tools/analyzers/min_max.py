"""
Module for local minima and maxima analysis on matrix data.

This module defines `MinMaxAnalyzer`, which splits each input CSV
matrix into smaller n×n blocks, identifies local minimum and maximum
positions within each block, aggregates the counts of these extrema
across the entire matrix, and saves both the flattened submatrix data
and the extrema index counts.
"""

import os

import numpy as np
import pandas as pd
from rich.progress import track

from .base import Analyzer


class MinMaxAnalyzer(Analyzer):
    """
    Analyzer for finding local minima and maxima in submatrices.

    This analyzer reads each CSV file as a square matrix (dropping rows
    if necessary to make it divisible by `matrix_size`), splits the
    matrix into non-overlapping `matrix_size`×`matrix_size` blocks,
    locates the min and max indices within each block, aggregates the
    counts of these indices, and saves both the index counts and the
    flattened submatrix data.

    Parameters
    ----------
    data_container : AnalysisData, optional
        Container for storing analysis outputs. If None, a new
        `AnalysisData` instance is created.
    """

    def __init__(self, data_container=None):
        super().__init__(data_container)

    def analyze(self, datasets, matrix_size=3):
        """
        Process a list of CSV datasets for min/max analysis.

        Iterates over each file path in `datasets`, invoking the
        internal `_process_minmax` method with the specified block size.

        Parameters
        ----------
        datasets : list of str
            Paths to CSV files containing square matrices (with an
            indexed "DataLine" column).
        matrix_size : int, default 3
            Size `n` of the submatrix blocks (n×n) to analyze.

        Returns
        -------
        None
        """
        for file_path in track(datasets, description="[green]Processing minmax..."):
            self._process_minmax(file_path, matrix_size)

    def _return_min_max_ix(self, m):
        """
        Find the indices of the minimum and maximum entries in a matrix.

        Parameters
        ----------
        m : numpy.ndarray
            2D array representing a submatrix.

        Returns
        -------
        list of int
            A list `[min_row, min_col, max_row, max_col]` giving the
            row and column indices of the minimum and maximum values.

        """
        min_ix = np.unravel_index(m.argmin(), m.shape)
        max_ix = np.unravel_index(m.argmax(), m.shape)
        return [min_ix[0], min_ix[1], max_ix[0], max_ix[1]]

    def _process_minmax(self, file_path, n=3):
        """
        Perform min/max extraction on a single CSV matrix.

        Reads the CSV into a DataFrame indexed by "DataLine", ensures the
        matrix is square and divisible by `n`, splits it into `n×n`
        blocks, flattens each block, computes local min/max indices,
        aggregates counts of these extrema positions, stores results in
        the shared data container, and writes two CSV outputs:
          - `<file>_min_max_ix(n×n).csv` containing aggregated counts
          - `<file>_flattened_submat(n×n).csv` containing flattened blocks

        Parameters
        ----------
        file_path : str
            Path to the CSV file. The CSV must have a "DataLine" column
            and the rest numeric columns forming a square matrix.
        n : int, default 3
            Block size for submatrices.

        Raises
        ------
        ValueError
            If the computed number of rows to drop is negative, if the
            trimmed matrix is not square, or if its dimension is not
            divisible by `n`.

        Returns
        -------
        None
        """
        data = pd.read_csv(file_path, index_col="DataLine")
        # Determine rows to drop to make square divisible by n
        rows_to_drop = data.shape[0] - int(data.shape[0] / n) * n
        if rows_to_drop < 0:
            raise ValueError("Number of rows to drop cannot be negative.")
        if rows_to_drop == 0:
            mat = data.to_numpy()
        else:
            mat = data.iloc[:-rows_to_drop, :-rows_to_drop].to_numpy()

        if mat.shape[0] != mat.shape[1]:
            raise ValueError("Check the dimension of main square matrix.")
        if mat.shape[0] % n != 0:
            raise ValueError("Check the dimension of smaller square matrix.")

        # Split into n×n blocks
        mat_list = []
        i1 = 0
        i2 = n
        while i2 <= mat.shape[0]:
            j1 = 0
            j2 = n
            while j2 <= mat.shape[1]:
                mat_list.append(mat[i1:i2, j1:j2])
                j1 += n
                j2 += n
            i1 += n
            i2 += n

        # Flatten each block into a DataFrame
        sub_mat_df = pd.DataFrame(
            [block.flatten() for block in mat_list],
            columns=[f"ri_{i}_ci_{j}" for i in range(n) for j in range(n)],
        )

        # Compute min/max indices for each block
        min_max_ix_dict = {
            idx + 1: self._return_min_max_ix(block) for idx, block in enumerate(mat_list)
        }
        points = pd.DataFrame.from_dict(min_max_ix_dict, orient="index")
        points = points.rename(columns={0: "min_r", 1: "min_c", 2: "max_r", 3: "max_c"})

        # Aggregate counts of minima and maxima positions
        min_df = points.groupby(["min_r", "min_c"]).size().reset_index()
        min_df = min_df.rename(columns={0: "X3", "min_r": "r", "min_c": "c"})
        min_df["type"] = "min"

        max_df = points.groupby(["max_r", "max_c"]).size().reset_index()
        max_df = max_df.rename(columns={0: "X3", "max_r": "r", "max_c": "c"})
        max_df["type"] = "max"

        agg_points = pd.concat([min_df, max_df])

        # Store in shared data container
        self.data.add_minmax_data(file_path, agg_points)

        # Save outputs
        base_path = os.path.dirname(file_path)
        agg_points.to_csv(os.path.join(base_path, f"min_max_ix({n}x{n}).csv"), index=False)
        sub_mat_df.to_csv(os.path.join(base_path, f"flattened_submat({n}x{n}).csv"), index=False)
