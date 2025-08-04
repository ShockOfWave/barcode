"""
Persistence homology analysis tools.

This module provides the :class:`PersistenceAnalyzer` class which
computes GUDHI persistence diagrams from CSV point‑cloud distance
matrices, stores them in a shared data container, exports a DataFrame
of birth–death intervals and generates both barcode and persistence
diagram plots.  The interface has been redesigned to decouple
computation from plotting and saving, allowing clients to consume raw
results without generating plots and deferring image generation to
frontends.
"""

from __future__ import annotations

import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import gudhi
from typing import List, Optional, Tuple
from rich.progress import track

from .base import Analyzer


def _convert_height_to_distance_matrix(df: pd.DataFrame) -> np.ndarray:
    """
    Преобразует матрицу высот в матрицу расстояний для персистентной гомологии.
    
    Parameters
    ----------
    df : pd.DataFrame
        Матрица высот
        
    Returns
    -------
    np.ndarray
        Матрица расстояний
    """
    # Преобразуем DataFrame в numpy array
    if isinstance(df, pd.DataFrame):
        X = df.to_numpy()
    else:
        X = df
    
    # Создаем точки в 3D пространстве (x, y, height)
    rows, cols = X.shape
    points = []
    
    for i in range(rows):
        for j in range(cols):
            points.append([i, j, X[i, j]])
    
    points = np.array(points)
    
    # Вычисляем матрицу расстояний между всеми точками
    from scipy.spatial.distance import pdist, squareform
    distances = pdist(points)
    distance_matrix = squareform(distances)
    
    return distance_matrix


class PersistenceAnalyzer(Analyzer):
    """
    Persistence homology analyzer for AFM data.

    This analyzer computes persistent homology using the GUDHI library.
    It converts height data into a distance matrix and computes the
    Rips complex to extract topological features.

    The persistence diagram shows the birth and death times of
    topological features (connected components, loops, voids) and
    can reveal the underlying structure of the surface.

    Attributes
    ----------
    data : object, optional
        Shared data container for storing results.
    plt_config : object
        Matplotlib configuration object for consistent plotting.
    """

    def __init__(self, data_container: Optional[object] = None) -> None:
        super().__init__(data_container)

    def compute(self, file_path: str, max_edge_length: float) -> Tuple[List[Tuple[int, Tuple[float, float]]], pd.DataFrame]:
        """
        Compute persistence homology for a single dataset.

        Parameters
        ----------
        file_path : str
            Path to the CSV or TXT file to analyze.
        max_edge_length : float
            Maximum edge length parameter for the Rips complex.

        Returns
        -------
        tuple
            A tuple ``(diag, diag_df)`` where ``diag`` is the raw
            persistence diagram (list of ``(dimension, (birth, death))``)
            and ``diag_df`` is a pandas DataFrame with columns
            ``Start``, ``End``, ``Length`` and ``Homology group``.
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
            # Для CSV файлов используем стандартное чтение
            df = pd.read_csv(file_path)
        
        # Преобразуем данные высоты в матрицу расстояний
        X = _convert_height_to_distance_matrix(df)
        
        # compute persistence diagram using GUDHI
        gudhi.persistence_graphical_tools._gudhi_matplotlib_use_tex = False
        rips_complex = gudhi.RipsComplex(distance_matrix=X, max_edge_length=max_edge_length)
        simplex_tree = rips_complex.create_simplex_tree(max_dimension=3)
        diag = simplex_tree.persistence(min_persistence=0)
        
        # store raw diagram
        if hasattr(self, 'data') and self.data is not None:
            self.data.add_persistence_diagram(file_path, diag)
        # convert to DataFrame
        records = [self._to_interval_record(dim, birth_death) for dim, birth_death in diag]
        diag_df = pd.DataFrame(records, columns=["Start", "End", "Length", "Homology group"])
        return diag, diag_df

    # -- high level API for CLI -------------------------------------------
    def analyze(self, datasets: List[str], max_edge_length: float) -> None:
        """
        Compute and save persistence diagrams for each dataset.

        Iterates over each CSV file path in ``datasets``, invokes
        :meth:`compute` and writes the resulting interval DataFrame and
        plots to disk.  This method mirrors the original behaviour for
        command line use but now uses the compute/save paradigm.

        Parameters
        ----------
        datasets : list of str
            Paths to CSV files representing distance matrices or point‑cloud
            data.
        max_edge_length : float
            Maximum edge length parameter for the Rips complex.
        """
        for file_path in track(datasets, description="[green]Processing persistence..."):
            diag, diag_df = self.compute(file_path, max_edge_length)
            # save interval DataFrame and plots
            self.save_results(file_path, diag, diag_df)

    # -- save --------------------------------------------------------------
    def save_results(self, file_path: str, diag: List[Tuple[int, Tuple[float, float]]], diag_df: pd.DataFrame, save_plots: bool = True) -> None:
        """
        Persist persistence analysis results to disk.

        Writes the interval DataFrame to ``diag_df_output.csv`` in the
        dataset's directory.  If ``save_plots`` is ``True`` barcode and
        persistence diagram plots are generated and saved as PNG, SVG
        and PDF.

        Parameters
        ----------
        file_path : str
            Original CSV file path.
        diag : list
            Raw persistence diagram as returned from :func:`compute`.
        diag_df : pandas.DataFrame
            DataFrame of persistence intervals.
        save_plots : bool, optional
            Whether to generate and save plots.  Default is ``True``.
        """
        base_path = os.path.dirname(file_path)
        # save DataFrame
        diag_df.to_csv(os.path.join(base_path, "diag_df_output.csv"), index=False)
        if save_plots:
            # number of intervals (used to limit bars/dots)
            diag_len = len(diag)
            fig_bar = self.plot_barcode(diag, diag_len)
            for ext in ("png", "svg", "pdf"):
                fig_bar.savefig(os.path.join(base_path, f"barcode.{ext}"), format=ext, dpi=1200, bbox_inches="tight")
            plt.close(fig_bar)
            fig_diag = self.plot_persistence_diagram(diag, diag_len)
            for ext in ("png", "svg", "pdf"):
                fig_diag.savefig(
                    os.path.join(base_path, f"persistence_diagram.{ext}"),
                    format=ext,
                    dpi=1200,
                    bbox_inches="tight",
                )
            plt.close(fig_diag)

    # -- plotting ----------------------------------------------------------
    def plot_barcode(self, diag: List[Tuple[int, Tuple[float, float]]], diag_length: int):
        """
        Generate a persistence barcode plot.

        Parameters
        ----------
        diag : list
            Persistence diagram to plot.
        diag_length : int
            Number of intervals; used to cap the number of bars drawn.

        Returns
        -------
        matplotlib.figure.Figure
            A figure containing the barcode plot.
        """
        self.plt_config.apply()
        fig = plt.figure()
        gudhi.plot_persistence_barcode(diag, fontsize=18, legend=True, inf_delta=0.5, max_intervals=diag_length + 1)
        plt.xlabel("Sampling length, nm", fontsize=16)
        plt.ylabel("Topological invariants", fontsize=18)
        plt.xticks(fontsize=16)
        plt.yticks(fontsize=0)
        return fig

    def plot_persistence_diagram(self, diag: List[Tuple[int, Tuple[float, float]]], diag_length: int):
        """
        Generate a persistence diagram plot.

        Parameters
        ----------
        diag : list
            Persistence diagram to plot.
        diag_length : int
            Number of intervals; used to cap the number of points drawn.

        Returns
        -------
        matplotlib.figure.Figure
            A figure containing the persistence diagram plot.
        """
        self.plt_config.apply()
        fig = plt.figure()
        gudhi.plot_persistence_diagram(
            diag,
            fontsize=18,
            alpha=0.5,
            legend=True,
            inf_delta=0.2,
            greyblock=False,
            max_intervals=diag_length + 1,
        )
        plt.xlabel("Feature appearance, nm", fontsize=18)
        plt.ylabel("Feature disappearance, nm", fontsize=18)
        plt.xticks(fontsize=16)
        plt.yticks(fontsize=16)
        return fig

    # -- helper ------------------------------------------------------------
    @staticmethod
    def _to_interval_record(dim: int, birth_death: Tuple[float, float]) -> Tuple[float, float, float, int]:
        """
        Convert a persistence interval into a record.

        Parameters
        ----------
        dim : int
            Homology dimension of the interval.
        birth_death : tuple
            Pair ``(birth, death)``.

        Returns
        -------
        tuple
            ``(birth, death, abs(birth - death), dim)``.
        """
        birth, death = birth_death
        return birth, death, abs(birth - death), dim