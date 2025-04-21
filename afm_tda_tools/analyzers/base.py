"""
Base module for analysis tools.

This module defines the `Analyzer` base class, which provides common utilities
for collecting CSV files, managing a shared data container, and defining the
interface for analysis and result saving.

Classes
-------
Analyzer
    Abstract base class for all analysis routines.
"""

import os

from afm_tda_tools.config import MatplotlibConfig
from afm_tda_tools.data import AnalysisData


class Analyzer:
    """
    Abstract base class for analyzers.

    Provides common functionality for:
      - configuring Matplotlib via `MatplotlibConfig`
      - managing a shared `AnalysisData` container
      - collecting input files
      - defining the interface for analysis and saving results

    Parameters
    ----------
    data_container : AnalysisData, optional
        Container for storing analysis outputs. If `None`, a new
        `AnalysisData` instance is created.
    """

    def __init__(self, data_container=None):
        self.plt_config = MatplotlibConfig()
        self.data = data_container if data_container else AnalysisData()

    def get_files(self, path_to_data, exclude_patterns=None):
        """
        Recursively collect CSV files from a directory, excluding by pattern.

        Parameters
        ----------
        path_to_data : str
            Path to the root directory to search for CSV files.
        exclude_patterns : list of str, optional
            List of filename suffixes to exclude. If None, no exclusions
            are applied.

        Returns
        -------
        list of str
            Paths to all CSV files under `path_to_data` that do not end
            with any of the given `exclude_patterns`.
        """
        files_list = []
        if exclude_patterns is None:
            exclude_patterns = []

        for root, _, files in os.walk(path_to_data):
            for file in files:
                if file.endswith(".csv") and not any(
                    file.endswith(pattern) for pattern in exclude_patterns
                ):
                    files_list.append(os.path.join(root, file))
        return files_list

    def analyze(self, datasets):
        """
        Perform analysis on a list of dataset files.

        Subclasses must override this method to implement specific analysis
        routines.

        Parameters
        ----------
        datasets : list of str
            List of dataset file paths to analyze.

        Raises
        ------
        NotImplementedError
            Always; subclasses must implement this method.
        """
        raise NotImplementedError("Subclasses must implement analyze method")

    def save_results(self, output_path):
        """
        Save analysis results to the specified directory.

        Subclasses must override this method to persist their results
        (plots, CSVs, etc.).

        Parameters
        ----------
        output_path : str
            Directory path where results should be saved.

        Raises
        ------
        NotImplementedError
            Always; subclasses must implement this method.
        """
        raise NotImplementedError("Subclasses must implement save_results method")
