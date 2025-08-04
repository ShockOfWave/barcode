"""
Base classes for analysis tools.

This module defines :class:`Analyzer`, an abstract base class that
provides common utilities for collecting CSV files, managing a shared
data container and defining the interface for analysis routines.  It
mirrors the original implementation but adds type hints and clearer
separation of responsibilities.  Subclasses override
:meth:`analyze` to perform their specific computations and
:meth:`save_results` to persist outputs.  Separating the compute
logic from the persistence allows results to be returned to a caller
without immediate file I/O.
"""

from __future__ import annotations

import os
from typing import List, Optional

from afm_tda_tools.config import MatplotlibConfig
from afm_tda_tools.data.data import AnalysisData


class Analyzer:
    """
    Abstract base class for analyzers.

    Provides common functionality for:
      * configuring Matplotlib via :class:`MatplotlibConfig`
      * managing a shared :class:`AnalysisData` container
      * collecting input files
      * defining the interface for analysis and result saving

    Parameters
    ----------
    data_container : AnalysisData, optional
        Container for storing analysis outputs.  If ``None``, a new
        :class:`AnalysisData` instance is created.
    """

    def __init__(self, data_container: Optional[AnalysisData] = None) -> None:
        self.plt_config = MatplotlibConfig()
        self.data = data_container if data_container else AnalysisData()

    def get_files(self, path_to_data: str, exclude_patterns: Optional[List[str]] = None) -> List[str]:
        """
        Recursively collect CSV files from a directory, excluding by pattern.

        Parameters
        ----------
        path_to_data : str
            Path to the root directory to search for CSV files.
        exclude_patterns : list of str, optional
            List of filename suffixes to exclude.  If ``None``, no exclusions
            are applied.

        Returns
        -------
        list of str
            Paths to all CSV files under ``path_to_data`` that do not end
            with any of the given ``exclude_patterns``.
        """
        files_list: List[str] = []
        if exclude_patterns is None:
            exclude_patterns = []

        for root, _, files in os.walk(path_to_data):
            for file in files:
                if file.endswith(".csv") and not any(file.endswith(pattern) for pattern in exclude_patterns):
                    files_list.append(os.path.join(root, file))
        return files_list

    def analyze(self, datasets: List[str], **kwargs) -> None:
        """
        Perform analysis on a list of dataset files.

        Subclasses must override this method to implement specific analysis
        routines.

        Parameters
        ----------
        datasets : list of str
            List of dataset file paths to analyze.
        kwargs : dict
            Additional keyword arguments specific to the analysis.

        Raises
        ------
        NotImplementedError
            Always; subclasses must implement this method.
        """
        raise NotImplementedError("Subclasses must implement analyze method")

    def save_results(self, output_path: str) -> None:
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