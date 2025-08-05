"""
Local minima and maxima analysis tools.

This module defines the :class:`MinMaxAnalyzer`, which splits each
input CSV matrix into smaller blocks, identifies local minima and maxima
within each block and aggregates counts of these extrema across the
entire matrix.  The API exposes a compute method that returns the
aggregated DataFrame and the flattened submatrices, and a save method
that writes results to disk.  This decoupling makes the computation
usable outside of CLI scripts.
"""

from __future__ import annotations

import os
import pandas as pd
import numpy as np
from typing import List, Optional, Tuple
from rich.progress import track

from .base import Analyzer


def _convert_data_to_expected_format(df: pd.DataFrame) -> pd.DataFrame:
    """
    Преобразует матрицу данных в формат, ожидаемый min-max анализатором.
    
    Parameters
    ----------
    df : pd.DataFrame
        Исходная матрица данных
        
    Returns
    -------
    pd.DataFrame
        DataFrame с индексом DataLine
    """
    # Если данные уже в нужном формате, возвращаем как есть
    if df.index.name == 'DataLine' or 'DataLine' in df.columns:
        return df
    
    # Преобразуем матрицу в нужный формат
    result_df = df.copy()
    result_df.index.name = 'DataLine'
    
    return result_df


class MinMaxAnalyzer(Analyzer):
    """
    Min-max analyzer for AFM data.

    This analyzer finds local minima and maxima in AFM height data by
    dividing the data into submatrices and identifying extrema within
    each block. It provides information about the distribution of
    surface features.

    The analysis helps characterize surface roughness and identify
    patterns in the height distribution.

    Attributes
    ----------
    data : object, optional
        Shared data container for storing results.
    plt_config : object
        Matplotlib configuration object for consistent plotting.
    """

    def __init__(self, data_container: Optional[object] = None) -> None:
        super().__init__(data_container)

    def compute(self, file_path: str, matrix_size: int = 3) -> Tuple[pd.DataFrame, pd.DataFrame]:
        """
        Compute min/max analysis for a single dataset.

        Parameters
        ----------
        file_path : str
            Path to the CSV or TXT file to analyze.
        matrix_size : int, optional
            Size of the submatrix blocks to analyze. Default is 3.

        Returns
        -------
        tuple
            A tuple ``(agg_points, sub_mat_df)`` where ``agg_points`` is a
            DataFrame with columns ``r``, ``c``, ``X3`` and ``type``
            describing the counts of minima and maxima positions, and
            ``sub_mat_df`` contains the flattened submatrices.  Both
            DataFrames are stored in the shared data container.
        """
        # Определяем формат файла и читаем данные
        if file_path.endswith('.txt'):
            # Для .txt файлов читаем как матрицу
            try:
                # Пропускаем комментарии и читаем данные
                data = []
                with open(file_path, 'r') as f:
                    for line in f:
                        line = line.strip()
                        if line and not line.startswith('#'):
                            # Разбиваем по табуляции или пробелам
                            values = line.split()
                            if values:
                                data.append([float(v) for v in values])
                
                if not data:
                    raise ValueError("No valid data found in file")
                
                df = pd.DataFrame(data)
            except Exception as e:
                raise ValueError(f"Error reading TXT file: {e}")
        else:
            # Для CSV файлов используем стандартное чтение без заголовков
            df = pd.read_csv(file_path, header=None)
        
        # Преобразуем данные в нужный формат
        data = _convert_data_to_expected_format(df)

        # Drop potential DataLine column for square matrix operations
        if 'DataLine' in data.columns:
            matrix = data.drop(columns=['DataLine'])
        else:
            matrix = data

        # Determine rows to drop to make square divisible by n
        rows_to_drop = matrix.shape[0] - int(matrix.shape[0] / matrix_size) * matrix_size
        if rows_to_drop < 0:
            raise ValueError("Number of rows to drop cannot be negative.")
        if rows_to_drop == 0:
            mat = matrix.to_numpy()
        else:
            mat = matrix.iloc[:-rows_to_drop, :-rows_to_drop].to_numpy()
        if mat.shape[0] != mat.shape[1]:
            raise ValueError("Check the dimension of main square matrix.")
        if mat.shape[0] % matrix_size != 0:
            raise ValueError("Check the dimension of smaller square matrix.")
        # split into n×n blocks
        mat_list: List[np.ndarray] = []
        for i1 in range(0, mat.shape[0], matrix_size):
            for j1 in range(0, mat.shape[1], matrix_size):
                mat_list.append(mat[i1:i1 + matrix_size, j1:j1 + matrix_size])
        # Flatten each block into a DataFrame
        sub_mat_df = pd.DataFrame(
            [block.flatten() for block in mat_list],
            columns=[f"ri_{i}_ci_{j}" for i in range(matrix_size) for j in range(matrix_size)],
        )
        # Compute min/max indices for each block
        min_max_ix_dict = {idx + 1: self._return_min_max_ix(block) for idx, block in enumerate(mat_list)}
        points = pd.DataFrame.from_dict(min_max_ix_dict, orient="index")
        points = points.rename(columns={0: "min_r", 1: "min_c", 2: "max_r", 3: "max_c"})
        # Aggregate counts
        min_df = points.groupby(["min_r", "min_c"]).size().reset_index()
        min_df = min_df.rename(columns={0: "X3", "min_r": "r", "min_c": "c"})
        min_df["type"] = "min"
        max_df = points.groupby(["max_r", "max_c"]).size().reset_index()
        max_df = max_df.rename(columns={0: "X3", "max_r": "r", "max_c": "c"})
        max_df["type"] = "max"
        agg_points = pd.concat([min_df, max_df], ignore_index=True)
        # Store in shared data container
        if hasattr(self, 'data') and self.data is not None:
            self.data.add_minmax_data(file_path, agg_points)
        return agg_points, sub_mat_df

    # -- high level API for CLI -------------------------------------------
    def analyze(self, datasets: List[str], matrix_size: int = 3) -> None:
        """
        Process a list of CSV datasets for min/max analysis and save results.

        Parameters
        ----------
        datasets : list of str
            Paths to CSV files containing square matrices (with an indexed
            ``DataLine`` column).
        matrix_size : int, optional
            Size ``n`` of the submatrix blocks (``n×n``) to analyze.
            Default is ``3``.
        """
        for file_path in track(datasets, description="[green]Processing minmax..."):
            agg_points, sub_mat_df = self.compute(file_path, matrix_size)
            self.save_results(file_path, agg_points, sub_mat_df, matrix_size)

    # -- save --------------------------------------------------------------
    def save_results(self, file_path: str, agg_points: pd.DataFrame, sub_mat_df: pd.DataFrame, matrix_size: int) -> None:
        """
        Persist min/max analysis results to disk.

        Writes the aggregated counts of extrema positions and the flattened
        submatrices to CSV files in the same directory as the input
        file.  The filenames include the block size for clarity.

        Parameters
        ----------
        file_path : str
            Original CSV file path.
        agg_points : pandas.DataFrame
            DataFrame of aggregated minima and maxima counts.
        sub_mat_df : pandas.DataFrame
            DataFrame of flattened submatrices.
        matrix_size : int
            Block size used in the computation.
        """
        base_path = os.path.dirname(file_path)
        agg_points.to_csv(os.path.join(base_path, f"min_max_ix({matrix_size}x{matrix_size}).csv"), index=False)
        sub_mat_df.to_csv(os.path.join(base_path, f"flattened_submat({matrix_size}x{matrix_size}).csv"), index=False)

    # -- internal helper ---------------------------------------------------
    @staticmethod
    def _return_min_max_ix(m: np.ndarray) -> List[int]:
        """
        Find the indices of the minimum and maximum entries in a matrix.

        Parameters
        ----------
        m : numpy.ndarray
            2D array representing a submatrix.

        Returns
        -------
        list of int
            A list ``[min_row, min_col, max_row, max_col]`` giving the
            row and column indices of the minimum and maximum values.
        """
        min_ix = np.unravel_index(m.argmin(), m.shape)
        max_ix = np.unravel_index(m.argmax(), m.shape)
        return [min_ix[0], min_ix[1], max_ix[0], max_ix[1]]