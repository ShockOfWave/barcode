"""
Data container for analysis outputs.

This module provides the :class:`AnalysisData` class which acts as a
centralised store for intermediate and final results produced by the
various analysis steps.  The original repository stored persistence
diagrams, autocorrelation data and min–max statistics in simple
dictionaries.  The API remains the same here to ensure backwards
compatibility.

The separation into a dedicated class makes it easier to expose the
raw results to other parts of an application, for example when
building a web service.  You can access data using
:py:meth:`get_persistence_diagram`, :py:meth:`get_acf_data` and
:py:meth:`get_minmax_data`.
"""

from __future__ import annotations

from typing import Dict, List, Tuple


class AnalysisData:
    """
    Container for analysis outputs.

    Provides methods to add and retrieve results from different analysis
    steps, keyed by the source file path.

    Attributes
    ----------
    persistence_diagrams : dict
        Maps file paths (str) to persistence diagrams (list of tuples).
    acf_data : dict
        Maps file paths (str) to autocorrelation result DataFrames.
    minmax_data : dict
        Maps file paths (str) to min–max analysis result DataFrames.
    """

    def __init__(self) -> None:
        self.persistence_diagrams: Dict[str, List[Tuple[int, Tuple[float, float]]]] = {}
        self.acf_data: Dict[str, object] = {}
        self.minmax_data: Dict[str, object] = {}

    def add_persistence_diagram(self, file_path: str, diagram: List[Tuple[int, Tuple[float, float]]]) -> None:
        """
        Store a persistence diagram for a given file.

        Parameters
        ----------
        file_path : str
            Path to the input CSV file associated with the diagram.
        diagram : list of tuple
            Persistence diagram as returned by GUDHI, i.e.
            a list of ``(dimension, (birth, death))`` tuples.
        """
        self.persistence_diagrams[file_path] = diagram

    def add_acf_data(self, file_path: str, acf_data: object) -> None:
        """
        Store autocorrelation data for a given file.

        Parameters
        ----------
        file_path : str
            Path to the input CSV file associated with the ACF data.
        acf_data : pandas.DataFrame
            DataFrame containing autocorrelation function values and metadata.
        """
        self.acf_data[file_path] = acf_data

    def add_minmax_data(self, file_path: str, minmax_data: object) -> None:
        """
        Store min–max analysis results for a given file.

        Parameters
        ----------
        file_path : str
            Path to the input CSV file associated with the min–max data.
        minmax_data : pandas.DataFrame
            DataFrame containing aggregated counts of local minima and
            maxima positions across submatrices.
        """
        self.minmax_data[file_path] = minmax_data

    def get_persistence_diagram(self, file_path: str):
        """Retrieve the stored persistence diagram for a file, or ``None``."""
        return self.persistence_diagrams.get(file_path)

    def get_acf_data(self, file_path: str):
        """Retrieve the stored autocorrelation data for a file, or ``None``."""
        return self.acf_data.get(file_path)

    def get_minmax_data(self, file_path: str):
        """Retrieve the stored min–max analysis data for a file, or ``None``."""
        return self.minmax_data.get(file_path)