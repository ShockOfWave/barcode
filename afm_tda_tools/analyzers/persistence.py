"""
Module for persistence homology analysis.

This module defines the `PersistenceAnalyzer` class, which computes
GUDHI persistence diagrams from CSV point-cloud data, stores them in
a shared data container, exports a DataFrame of birth–death intervals,
and generates both barcode and persistence diagram plots in PNG, SVG,
and PDF formats.
"""

import os

import gudhi
import matplotlib.pyplot as plt
import pandas as pd
from rich.progress import track

from .base import Analyzer


class PersistenceAnalyzer(Analyzer):
    """
    Analyzer for computing persistence diagrams and plots.

    This analyzer reads each CSV file into a NumPy array, builds a Rips
    complex up to dimension 3 with a user-specified edge length threshold,
    computes the persistence diagram, stores it in the shared data
    container, exports the diagram as a DataFrame, and saves both a
    barcode plot and a persistence diagram plot in multiple formats.

    Parameters
    ----------
    data_container : AnalysisData, optional
        Container for storing analysis outputs. If `None`, a new
        `AnalysisData` instance is created.
    """

    def __init__(self, data_container=None):
        super().__init__(data_container)

    def analyze(self, datasets, max_edge_length):
        """
        Compute and save persistence diagrams for each dataset.

        Iterates over each CSV file path in `datasets`, invoking
        `_process_persistence` with the specified `max_edge_length`.

        Parameters
        ----------
        datasets : list of str
            Paths to CSV files representing distance matrices or point-cloud
            data.
        max_edge_length : float
            Maximum edge length parameter for the Rips complex.
        """
        for file_path in track(datasets, description="[green]Processing persistence..."):
            self._process_persistence(file_path, max_edge_length)

    def _process_persistence(self, file_path, max_edge_length):
        """
        Compute persistence diagram and save results for one file.

        Reads the CSV file into a NumPy array, constructs a Rips complex,
        computes its persistence diagram, stores the raw diagram in the
        data container, exports a DataFrame of intervals, and saves
        barcode and persistence diagram plots.

        Parameters
        ----------
        file_path : str
            Path to the CSV file to analyze.
        max_edge_length : float
            Maximum edge length to use when building the Rips complex.

        Returns
        -------
        None
        """
        # Load data and compute persistence
        df = pd.read_csv(file_path)
        X = df.to_numpy()
        gudhi.persistence_graphical_tools._gudhi_matplotlib_use_tex = False
        rips_complex = gudhi.RipsComplex(distance_matrix=X, max_edge_length=max_edge_length)
        simplex_tree = rips_complex.create_simplex_tree(max_dimension=3)
        diag = simplex_tree.persistence(min_persistence=0)

        # Store raw diagram
        self.data.add_persistence_diagram(file_path, diag)

        # Save path
        base_path = os.path.dirname(file_path)

        # Export intervals as DataFrame
        records = self._extract_list_from_raw_data(diag)
        diag_df = pd.DataFrame(records, columns=["Start", "End", "Length", "Homology group"])
        diag_df.to_csv(os.path.join(base_path, "diag_df_output.csv"), index=False)

        # Save plots
        self._save_barcode(base_path, diag, len(records))
        self._save_persistence_diagram(base_path, diag, len(records))

    def _extract_list_from_raw_data(self, diagrams):
        """
        Convert raw GUDHI diagram into a list of intervals.

        Transforms a list of `(dim, (birth, death))` tuples into a list
        of records `[birth, death, |birth-death|, dim]`.

        Parameters
        ----------
        diagrams : list of tuple
            Persistence diagram as returned by `simplex_tree.persistence()`.

        Returns
        -------
        list of list
            Each inner list contains `[start, end, length, homology_group]`.
        """
        records = []
        for dim, (birth, death) in diagrams:
            records.append([birth, death, abs(birth - death), dim])
        return records

    def _save_barcode(self, base_path, diag, diag_length):
        """
        Generate and save a persistence barcode plot.

        Applies Matplotlib configuration, plots the barcode with a legend,
        and saves it as PNG, SVG, and PDF using high resolution.

        Parameters
        ----------
        file_path : str
            Original CSV file path used to derive base filenames.
        diag : list of tuple
            Persistence diagram to plot.
        diag_length : int
            Number of intervals in the diagram.

        Returns
        -------
        None
        """
        self.plt_config.apply()
        gudhi.plot_persistence_barcode(
            diag, fontsize=18, legend=True, inf_delta=0.5, max_intervals=diag_length + 1
        )
        plt.xlabel("Sampling length, nm", fontsize=16)
        plt.ylabel("Topological invariants", fontsize=18)
        plt.xticks(fontsize=16)
        plt.yticks(fontsize=0)

        for ext in ("png", "svg", "pdf"):
            plt.savefig(
                os.path.join(base_path, f"barcode.{ext}"), format=ext, dpi=1200, bbox_inches="tight"
            )

    def _save_persistence_diagram(self, base_path, diag, diag_length):
        """
        Generate and save a persistence diagram plot.

        Applies Matplotlib configuration, plots the persistence diagram
        with a legend, and saves it as PNG, SVG, and PDF using high resolution.

        Parameters
        ----------
        file_path : str
            Original CSV file path used to derive base filenames.
        diag : list of tuple
            Persistence diagram to plot.
        diag_length : int
            Number of intervals in the diagram.

        Returns
        -------
        None
        """
        self.plt_config.apply()
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

        for ext in ("png", "svg", "pdf"):
            plt.savefig(
                os.path.join(base_path, f"persistence_diagram.{ext}"),
                format=ext,
                dpi=1200,
                bbox_inches="tight",
            )
