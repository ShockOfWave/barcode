"""
Pairwise persistence diagram distance analysis tools.

This module defines the :class:`BottleneckAnalyzer`, which converts
persistence diagrams into NumPy arrays and computes pairwise bottleneck
and Wasserstein distances between all diagrams.  The results can be
returned to the caller as pandas DataFrames or written to disk.  The
compute/save separation allows the analysis to be integrated into
back‑end services where results may be serialised for clients.
"""

from __future__ import annotations

import os
import pandas as pd
import numpy as np
import gudhi
from gudhi.hera import bottleneck_distance, wasserstein_distance
from typing import Dict, Iterable, List, Optional, Tuple
from rich.progress import track

from .base import Analyzer


class BottleneckAnalyzer(Analyzer):
    """
    Bottleneck distance analyzer for AFM data.

    This analyzer computes bottleneck and Wasserstein distances between
    persistence diagrams. It can work with precomputed diagrams or
    compute them on the fly from height data.

    The bottleneck distance measures the similarity between two
    persistence diagrams and is useful for comparing topological
    features across different samples.

    Attributes
    ----------
    data : object, optional
        Shared data container for storing results.
    plt_config : object
        Matplotlib configuration object for consistent plotting.
    bottleneck_results : pd.DataFrame
        Matrix of bottleneck distances between datasets.
    wasserstein_results : pd.DataFrame
        Matrix of Wasserstein distances between datasets.
    """

    def __init__(self, data_container: Optional[object] = None) -> None:
        super().__init__(data_container)
        self.bottleneck_results = None
        self.wasserstein_results = None

    def compute(
        self,
        datasets: Iterable[str],
        diagrams: Optional[Dict[str, List[Tuple[int, Tuple[float, float]]]]] = None,
        delta: float = 0.01,
        order: float = 1.0,
        max_edge_length: float = 1.0,
    ) -> Tuple[pd.DataFrame, pd.DataFrame]:
        """
        Compute bottleneck and Wasserstein distance matrices.

        Parameters
        ----------
        datasets : iterable of str
            Paths to CSV or TXT files containing height data or
            references to precomputed diagrams.
        diagrams : dict, optional
            Precomputed persistence diagrams keyed by file path.  If
            provided, diagrams in the dictionary will be used; otherwise
            diagrams are computed on the fly using ``max_edge_length``.
        delta : float, optional
            Tolerance parameter for the bottleneck distance.  Default is
            ``0.01``.
        order : float, optional
            Order parameter for the Wasserstein distance.  Default is
            ``1.0``.
        max_edge_length : float, optional
            Maximum edge length to use when computing persistence diagrams
            on the fly.  Default is ``1.0``.

        Returns
        -------
        tuple
            ``(bn_df, ws_df)`` where ``bn_df`` and ``ws_df`` are pandas
            DataFrames containing pairwise bottleneck and Wasserstein
            distances, respectively.
        """
        names: List[str] = []
        diagrams_list: List[List[Tuple[int, Tuple[float, float]]]] = []
        # Collect persistence diagrams
        for path in track(list(datasets), description="[green]Preparing persistence diagrams..."):
            if diagrams and path in diagrams:
                diag = diagrams[path]
            else:
                # compute diagram on the fly using default max_edge_length
                diag = self._compute_persistence(path, max_edge_length)
            diagrams_list.append(diag)
            names.append(os.path.splitext(os.path.basename(path))[0])
        # Convert diagrams to arrays of shape (N, 2)
        arrays = [self._diag_to_array(d) for d in diagrams_list]
        # Compute pairwise distances and fill matrices
        bn_matrix = np.zeros((len(arrays), len(arrays)))
        ws_matrix = np.zeros((len(arrays), len(arrays)))
        for i, Xi in enumerate(arrays):
            for j, Xj in enumerate(arrays):
                bn_matrix[i, j] = bottleneck_distance(Xi, Xj, delta=delta)
                ws_matrix[i, j] = wasserstein_distance(Xi, Xj, order=order)
        bn_df = pd.DataFrame(bn_matrix, index=names, columns=names)
        ws_df = pd.DataFrame(ws_matrix, index=names, columns=names)
        # store results in instance attributes for compatibility
        self.bottleneck_results = bn_df
        self.wasserstein_results = ws_df
        return bn_df, ws_df

    def _compute_persistence(self, file_path: str, max_edge_length: float) -> List[Tuple[int, Tuple[float, float]]]:
        """
        Compute a persistence diagram directly from a CSV or TXT file.

        Parameters
        ----------
        file_path : str
            Path to the CSV or TXT file containing ACF data.
        max_edge_length : float
            Maximum edge length to use when building the Rips complex.

        Returns
        -------
        list of tuple
            Persistence diagram as returned by GUDHI's ``simplex_tree.persistence()``.
        """
        # Определяем формат файла и читаем данные
        if file_path.endswith('.txt'):
            # Для .txt файлов читаем как матрицу
            try:
                data = []
                with open(file_path, 'r') as f:
                    for line in f:
                        line = line.strip()
                        if line and not line.startswith('#'):
                            values = line.split()
                            if values:
                                data.append([float(v) for v in values])

                if not data:
                    raise ValueError("No valid data found in file")

                df = pd.DataFrame(data)
            except Exception as e:
                raise ValueError(f"Error reading TXT file: {e}")
        else:
            # Для CSV файлов используем стандартное чтение
            df = pd.read_csv(file_path)

        # Обрабатываем ACF данные - создаем точки из временного ряда
        if 'ACF' in df.columns and 'ix' in df.columns:
            # Это ACF данные - создаем точки (время, ACF значение)
            points = df[['ix', 'ACF']].values
            rips = gudhi.RipsComplex(points=points, max_edge_length=max_edge_length)
        else:
            # Предполагаем, что это матрица расстояний после предобработки
            if df.shape[1] == df.shape[0] + 1:
                df = df.drop(columns=df.columns[0])
            matrix = df.to_numpy()
            rips = gudhi.RipsComplex(distance_matrix=matrix, max_edge_length=max_edge_length)

        tree = rips.create_simplex_tree(max_dimension=3)
        return tree.persistence(min_persistence=0)

    # -- high level API for CLI -------------------------------------------
    def analyze(
        self,
        datasets: List[str],
        persistence_analyzer: Optional[object] = None,
        delta: float = 0.01,
        order: float = 1.0,
        save_path: Optional[str] = None,
    ) -> None:
        """Compute distance matrices for CLI and save to disk.

        Parameters
        ----------
        datasets : list of str
            Paths to CSV or TXT files containing height data.
        persistence_analyzer : PersistenceAnalyzer, optional
            If provided and contains diagrams for the datasets, those
            diagrams are reused; otherwise new diagrams are computed.
        delta : float, optional
            Tolerance parameter for the bottleneck distance.
        order : float, optional
            Order parameter for the Wasserstein distance.
        save_path : str, optional
            Directory where the resulting CSV files will be written. If
            not provided, the directory of the first dataset is used.
        """
        # if there are no datasets to analyse, simply return
        if not datasets:
            return
        # prepare precomputed diagrams if available
        diagrams = None
        if persistence_analyzer is not None:
            diagrams = persistence_analyzer.data.persistence_diagrams
        bn_df, ws_df = self.compute(datasets, diagrams=diagrams, delta=delta, order=order)
        # save to disk using the provided path or the directory of the first dataset
        save_dir = save_path if save_path is not None else os.path.dirname(datasets[0])
        self.save_results(save_dir, bn_df, ws_df)

    # -- save --------------------------------------------------------------
    def save_results(self, save_path: str, bn_df: pd.DataFrame, ws_df: pd.DataFrame) -> None:
        """
        Save computed distance matrices to CSV files.

        Creates ``save_path`` if it does not exist, then writes both
        bottleneck and Wasserstein results as:
        ``results_bottleneck.csv`` and ``results_wasserstein.csv``.

        Parameters
        ----------
        save_path : str
            Directory where result CSV files will be saved.
        bn_df : pandas.DataFrame
            Bottleneck distance matrix.
        ws_df : pandas.DataFrame
            Wasserstein distance matrix.
        """
        if not os.path.exists(save_path):
            os.makedirs(save_path, exist_ok=True)
        bn_df.to_csv(os.path.join(save_path, "results_bottleneck.csv"))
        ws_df.to_csv(os.path.join(save_path, "results_wasserstein.csv"))

    # -- helpers -----------------------------------------------------------
    @staticmethod
    def _diag_to_array(diag: List[Tuple[int, Tuple[float, float]]]) -> np.ndarray:
        """
        Convert a GUDHI persistence diagram to an ``(N, 2)`` array.

        Parameters
        ----------
        diag : list of tuple
            Persistence diagram as returned by ``simplex_tree.persistence()``.

        Returns
        -------
        numpy.ndarray
            Array of shape ``(N, 2)`` with dtype ``float64``, where each
            row corresponds to a ``(birth, death)`` pair.
        """
        points = [pair for _, pair in diag]
        return np.array(points, dtype=np.float64)