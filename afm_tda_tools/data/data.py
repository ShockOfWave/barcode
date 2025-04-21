"""
Module for storing and retrieving analysis results.

This module defines the `AnalysisData` class, which provides a centralized
container to hold persistence diagrams, autocorrelation data, and
min–max analysis outputs for each processed dataset.
"""


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

    def __init__(self):
        self.persistence_diagrams = {}
        self.acf_data = {}
        self.minmax_data = {}

    def add_persistence_diagram(self, file_path, diagram):
        """
        Store a persistence diagram for a given file.

        Parameters
        ----------
        file_path : str
            Path to the input CSV file associated with the diagram.
        diagram : list of tuple
            Persistence diagram as returned by GUDHI, i.e.
            a list of `(dimension, (birth, death))` tuples.

        Returns
        -------
        None
        """
        self.persistence_diagrams[file_path] = diagram

    def add_acf_data(self, file_path, acf_data):
        """
        Store autocorrelation data for a given file.

        Parameters
        ----------
        file_path : str
            Path to the input CSV file associated with the ACF data.
        acf_data : pandas.DataFrame
            DataFrame containing autocorrelation function values and
            metadata (lags, axis labels, etc.).

        Returns
        -------
        None
        """
        self.acf_data[file_path] = acf_data

    def add_minmax_data(self, file_path, minmax_data):
        """
        Store min–max analysis results for a given file.

        Parameters
        ----------
        file_path : str
            Path to the input CSV file associated with the min–max data.
        minmax_data : pandas.DataFrame
            DataFrame containing aggregated counts of local minima and
            maxima positions across submatrices.

        Returns
        -------
        None
        """
        self.minmax_data[file_path] = minmax_data

    def get_persistence_diagram(self, file_path):
        """
        Retrieve the stored persistence diagram for a file.

        Parameters
        ----------
        file_path : str
            Path to the input CSV file whose diagram is requested.

        Returns
        -------
        list of tuple or None
            The persistence diagram if present, otherwise `None`.
        """
        return self.persistence_diagrams.get(file_path)

    def get_acf_data(self, file_path):
        """
        Retrieve the stored autocorrelation data for a file.

        Parameters
        ----------
        file_path : str
            Path to the input CSV file whose ACF data is requested.

        Returns
        -------
        pandas.DataFrame or None
            The autocorrelation DataFrame if present, otherwise `None`.
        """
        return self.acf_data.get(file_path)

    def get_minmax_data(self, file_path):
        """
        Retrieve the stored min–max analysis data for a file.

        Parameters
        ----------
        file_path : str
            Path to the input CSV file whose min–max data is requested.

        Returns
        -------
        pandas.DataFrame or None
            The min–max analysis DataFrame if present, otherwise `None`.
        """
        return self.minmax_data.get(file_path)
