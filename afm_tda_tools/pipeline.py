"""
Module defining the analysis pipeline for AFM data processing.

This pipeline handles preprocessing of raw `.txt` files into CSV,
followed by sequential execution of:
  - autocorrelation analysis
  - persistence homology analysis
  - min–max analysis
  - bottleneck and Wasserstein distance computation

Results are stored in a shared AnalysisData container and exported
to the specified save directory.
"""

import os

from afm_tda_tools.analyzers import (
    AutocorrelationAnalyzer,
    BottleneckAnalyzer,
    MinMaxAnalyzer,
    PersistenceAnalyzer,
)
from afm_tda_tools.data import AnalysisData, txt_to_csv_folder


class AnalysisPipeline:
    """
    Orchestrates the full analysis workflow on AFM datasets.

    This class runs a sequence of analyzers on raw AFM data:
      1. Convert raw `.txt` files to CSV.
      2. Autocorrelation analysis.
      3. Persistence homology analysis.
      4. Min–max block-wise analysis.
      5. Pairwise bottleneck and Wasserstein distance computation.

    Parameters
    ----------
    data_path : str
        Path to the directory containing raw `.txt` files.
    save_path : str
        Path to the directory where processed CSV files and results
        will be saved.
    exclude_patterns : list of str, optional
        Filename suffixes to exclude from analysis (default:
        ["(3x3).csv", "_auto.csv", "output.csv"]).
    width_line : float, default 0.1
        Sampling interval (µm) for autocorrelation lag scaling.
    max_edge_length : float, default 1.0
        Maximum edge length for Rips complex construction.
    matrix_size : int, default 3
        Block size for min–max analysis.
    delta : float, default 0.01
        Tolerance for bottleneck distance computation.
    order : float, default 1.0
        Order for Wasserstein distance computation.
    """

    def __init__(
        self,
        data_path,
        save_path,
        exclude_patterns=None,
        width_line=0.1,
        max_edge_length=1.0,
        matrix_size=3,
        delta=0.01,
        order=1.0,
    ):
        self.data_path = data_path
        self.save_path = save_path
        self.exclude_patterns = (
            exclude_patterns
            if exclude_patterns is not None
            else ["(3x3).csv", "_auto.csv", "output.csv"]
        )

        # Shared container for intermediate and final results
        self.data_container = AnalysisData()

        # Initialize analyzers with the shared data container
        self.acf_analyzer = AutocorrelationAnalyzer(self.data_container)
        self.persistence_analyzer = PersistenceAnalyzer(self.data_container)
        self.minmax_analyzer = MinMaxAnalyzer(self.data_container)
        self.bottleneck_analyzer = BottleneckAnalyzer(self.data_container)

        # Default parameters for each analysis step
        self.width_line = width_line
        self.max_edge_length = max_edge_length
        self.matrix_size = matrix_size
        self.delta = delta
        self.order = order

    def run(self):
        """
        Execute the full analysis pipeline.

        This method performs the following steps in order:
          1. Preprocess raw `.txt` files into CSV.
          2. Collect processed CSV files, excluding any matching
             `exclude_patterns`.
          3. Run autocorrelation analysis.
          4. Run persistence homology analysis.
          5. Run min–max block-wise analysis.
          6. Compute and save bottleneck and Wasserstein distances.

        Returns
        -------
        None
        """
        # Step 0: preprocess raw text files
        txt_to_csv_folder(self.data_path, self.save_path)

        # Step 1: collect CSV files for analysis
        files = self.acf_analyzer.get_files(self.save_path, exclude_patterns=self.exclude_patterns)

        # Step 2: autocorrelation
        self.acf_analyzer.analyze(files, width_line=self.width_line)

        # Step 3: persistence diagrams and plots
        self.persistence_analyzer.analyze(files, max_edge_length=self.max_edge_length)

        # Step 4: min–max block-wise analysis
        self.minmax_analyzer.analyze(files, matrix_size=self.matrix_size)

        # Step 5: bottleneck and Wasserstein distances
        self.bottleneck_analyzer.analyze(
            files,
            persistence_analyzer=self.persistence_analyzer,
            delta=self.delta,
            order=self.order,
        )

        # Step 6: save bottleneck analysis results
        save_dir = os.path.join(self.save_path)
        self.bottleneck_analyzer.save_results(save_dir)

        print("Pipeline finished successfully.")
