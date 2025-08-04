"""
High level analysis pipeline.

The :class:`AnalysisPipeline` orchestrates the end‑to‑end workflow of the
AFM topological data analysis.  It performs the following steps:

1. Convert raw `.txt` files into CSV via :func:`afm_tda_tools.data.data_converter.txt_to_csv_folder`.
2. Collect processed CSV files, excluding any patterns supplied by the user.
3. Run autocorrelation analysis (compute + save).
4. Run persistence homology analysis (compute + save).
5. Run min–max block‑wise analysis (compute + save).
6. Compute bottleneck and Wasserstein distances and save the resulting
   matrices.

The pipeline leverages the compute/save separation implemented in each
analyzer.  While the CLI uses the default behaviour of saving results
locally, server applications can reuse the individual analyzers and
their compute methods to obtain raw results without writing to disk.
"""

from __future__ import annotations

import os
from typing import List, Optional

from afm_tda_tools.analyzers.autocorrelation import AutocorrelationAnalyzer
from afm_tda_tools.analyzers.persistence import PersistenceAnalyzer
from afm_tda_tools.analyzers.min_max import MinMaxAnalyzer
from afm_tda_tools.analyzers.bottleneck import BottleneckAnalyzer
from afm_tda_tools.data.data import AnalysisData
from afm_tda_tools.data.data_converter import txt_to_csv_folder


class AnalysisPipeline:
    """
    Orchestrate the full analysis workflow on AFM datasets.

    This class runs a sequence of analyzers on raw AFM data: conversion
    from `.txt` to `.csv`, autocorrelation analysis, persistence
    analysis, min–max analysis and finally pairwise diagram distances.

    Parameters
    ----------
    data_path : str
        Path to the directory containing raw `.txt` files.
    save_path : str
        Path to the directory where processed CSV files and results
        will be saved.
    exclude_patterns : list of str, optional
        Filename suffixes to exclude from analysis (default:
        ``["(3x3).csv", "_auto.csv", "output.csv"]``).
    width_line : float, optional
        Sampling interval (µm) for autocorrelation lag scaling.  Default
        is ``0.1``.
    max_edge_length : float, optional
        Maximum edge length for Rips complex construction.  Default is
        ``1.0``.
    matrix_size : int, optional
        Block size for min–max analysis.  Default is ``3``.
    delta : float, optional
        Tolerance for bottleneck distance computation.  Default is
        ``0.01``.
    order : float, optional
        Order for Wasserstein distance computation.  Default is ``1.0``.
    multiply_const : float, optional
        Scaling factor to apply to raw data values during preprocessing.
        Default is ``1e9``.
    """

    def __init__(
        self,
        data_path: str,
        save_path: str,
        exclude_patterns: Optional[List[str]] = None,
        width_line: float = 0.1,
        max_edge_length: float = 1.0,
        matrix_size: int = 3,
        delta: float = 0.01,
        order: float = 1.0,
        multiply_const: float = 1e9,
    ) -> None:
        self.data_path = data_path
        self.save_path = save_path
        self.exclude_patterns = (
            exclude_patterns if exclude_patterns is not None else ["(3x3).csv", "_auto.csv", "output.csv"]
        )
        self.multiply_const = multiply_const
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

    def run(self) -> None:
        """Execute the full analysis pipeline."""
        # Step 1: collect files for analysis (both .txt and .csv)
        files = []
        for root, _, filenames in os.walk(self.data_path):
            for filename in filenames:
                if filename.endswith(('.txt', '.csv')):
                    file_path = os.path.join(root, filename)
                    # Check if file should be excluded
                    if not any(filename.endswith(pattern) for pattern in self.exclude_patterns):
                        files.append(file_path)
        
        if not files:
            print("No files found for analysis.")
            return
        
        # Step 2: autocorrelation (compute + save)
        self.acf_analyzer.analyze(files, width_line=self.width_line)
        # Step 3: persistence diagrams (compute + save)
        self.persistence_analyzer.analyze(files, max_edge_length=self.max_edge_length)
        # Step 4: min–max block‑wise analysis (compute + save)
        self.minmax_analyzer.analyze(files, matrix_size=self.matrix_size)
        # Step 5: bottleneck and Wasserstein distances (compute + save)
        self.bottleneck_analyzer.analyze(
            files,
            persistence_analyzer=self.persistence_analyzer,
            delta=self.delta,
            order=self.order,
        )
        print("Pipeline finished successfully.")