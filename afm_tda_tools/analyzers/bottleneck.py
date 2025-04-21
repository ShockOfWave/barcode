"""
Module for computing pairwise persistence diagram distances.

This module provides the `BottleneckAnalyzer` class, which converts
GUDHI persistence diagrams into NumPy arrays and computes both
bottleneck and Wasserstein distances between all pairs of diagrams.
Results can be saved as CSV tables.
"""

import os

import gudhi
import numpy as np
import pandas as pd
from gudhi.hera import bottleneck_distance, wasserstein_distance
from rich.progress import track

from .base import Analyzer


class BottleneckAnalyzer(Analyzer):
    """
    Analyzer for pairwise persistence diagram distances.

    This analyzer collects persistence diagrams (either provided by a
    `PersistenceAnalyzer` or computed on the fly), converts them into
    Nx2 NumPy arrays of (birth, death), and computes the bottleneck
    and Wasserstein distances between every pair.

    Parameters
    ----------
    data_container : AnalysisData, optional
        Container for storing analysis outputs. If `None`, a new
        `AnalysisData` instance is created.

    Attributes
    ----------
    bottleneck_results : list of pandas.DataFrame
        List of DataFrames containing pairwise bottleneck distances.
    wasserstein_results : list of pandas.DataFrame
        List of DataFrames containing pairwise Wasserstein distances.
    """

    def __init__(self, data_container=None):
        super().__init__(data_container)
        self.bottleneck_results = []
        self.wasserstein_results = []

    @staticmethod
    def _diag_to_array(diag):
        """
        Convert a GUDHI persistence diagram to an (N, 2) array.

        Transforms a list of (dimension, (birth, death)) tuples into
        a NumPy array where each row is [birth, death].

        Parameters
        ----------
        diag : list of tuple
            Persistence diagram as returned by `simplex_tree.persistence()`,
            i.e. a list of tuples `(dim, (birth, death))`.

        Returns
        -------
        numpy.ndarray
            Array of shape (N, 2) with dtype float64, where each row
            corresponds to a (birth, death) pair.
        """
        points = [pair for _, pair in diag]
        return np.array(points, dtype=np.float64)

    def analyze(self, datasets, persistence_analyzer=None, delta=0.01, order=1.0):
        """
        Compute bottleneck and Wasserstein distance matrices.

        For each file in `datasets`, retrieves or computes its persistence
        diagram, converts all diagrams to NumPy arrays, and then computes
        two distance matrices:
          - bottleneck distances with tolerance `delta`
          - p-Wasserstein distances with order `order`

        Parameters
        ----------
        datasets : list of str
            Paths to CSV files containing point-cloud distance matrices or
            references to precomputed diagrams.
        persistence_analyzer : PersistenceAnalyzer, optional
            Analyzer instance that has already computed persistence diagrams.
            If provided and contains a diagram for a given path, that diagram
            will be reused; otherwise, it is computed on the fly.
        delta : float, default 0.01
            Tolerance parameter for the bottleneck distance.
        order : float, default 1.0
            Order parameter for the Wasserstein distance.

        Returns
        -------
        None
        """
        names = []
        diags = []

        # Collect persistence diagrams
        for path in track(datasets, description="[green]Preparing persistence diagrams..."):
            if persistence_analyzer and path in persistence_analyzer.data.persistence_diagrams:
                diag = persistence_analyzer.data.persistence_diagrams[path]
            else:
                diag = self._calc_only_persistence(path)
            diags.append(diag)
            names.append(os.path.splitext(os.path.basename(path))[0])

        # Convert diagrams to arrays of shape (N, 2)
        arrays = [self._diag_to_array(d) for d in diags]

        # Compute pairwise distances
        for i, Xi in track(enumerate(arrays), description="[green]Computing diagram distances..."):
            bottleneck_dist = []
            wasserstein_dist = []

            for Xj in arrays:
                bn = bottleneck_distance(Xi, Xj, delta=delta)
                ws = wasserstein_distance(Xi, Xj, order=order)
                bottleneck_dist.append(bn)
                wasserstein_dist.append(ws)

            idx = names[i]
            cols = names
            self.bottleneck_results.append(
                pd.DataFrame([bottleneck_dist], index=[idx], columns=cols)
            )
            self.wasserstein_results.append(
                pd.DataFrame([wasserstein_dist], index=[idx], columns=cols)
            )

    def _calc_only_persistence(self, file_path):
        """
        Compute persistence diagram directly from a CSV distance matrix.

        Reads a CSV file into a NumPy array, constructs a Rips complex
        with default max_edge_length of 1.0, and returns its persistence
        diagram.

        Parameters
        ----------
        file_path : str
            Path to the CSV file containing a square distance matrix.

        Returns
        -------
        list of tuple
            Persistence diagram as returned by GUDHI's `simplex_tree.persistence()`.
        """
        df = pd.read_csv(file_path)
        X = df.to_numpy()
        rips = gudhi.RipsComplex(distance_matrix=X, max_edge_length=1.0)
        tree = rips.create_simplex_tree(max_dimension=3)
        return tree.persistence(min_persistence=0)

    def save_results(self, save_path):
        """
        Save computed distance matrices to CSV files.

        Creates `save_path` if it does not exist, then concatenates and
        writes both bottleneck and Wasserstein results as:
          - results_bottleneck.csv
          - results_wasserstein.csv

        Parameters
        ----------
        save_path : str
            Directory where result CSV files will be saved.

        Returns
        -------
        None
        """
        if not os.path.exists(save_path):
            os.makedirs(save_path, exist_ok=True)

        pd.concat(self.bottleneck_results).to_csv(os.path.join(save_path, "results_bottleneck.csv"))
        pd.concat(self.wasserstein_results).to_csv(
            os.path.join(save_path, "results_wasserstein.csv")
        )
