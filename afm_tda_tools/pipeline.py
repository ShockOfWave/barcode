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
        grid_size: Optional[int] = None,
    ) -> None:
        self.data_path = data_path
        parent = os.path.dirname(save_path)
        if parent and not os.path.isdir(parent):
            raise FileNotFoundError(f"Parent directory {parent} does not exist")
        os.makedirs(save_path, exist_ok=True)
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
        self.grid_size = grid_size

    def run(self) -> None:
        """Execute the full analysis pipeline."""
        if not os.path.isdir(self.data_path):
            raise FileNotFoundError(f"Data path {self.data_path} does not exist")

        # Step 1: preprocess raw txt files into CSV under save_path
        txt_to_csv_folder(
            self.data_path,
            self.save_path,
            multiply_const=self.multiply_const,
            grid_size=self.grid_size,
            exclude_patterns=self.exclude_patterns,
        )

        # Step 2: collect processed CSV files
        files = []
        for root, _, filenames in os.walk(self.save_path):
            for filename in filenames:
                if filename.endswith('.csv') and not any(
                    filename.endswith(pattern) for pattern in self.exclude_patterns
                ):
                    files.append(os.path.join(root, filename))
        
        if not files:
            print("No files found for analysis.")
            return

        # Step 3 onwards: run analyzers on processed files
        # Autocorrelation (compute + save)
        self.acf_analyzer.analyze(files, width_line=self.width_line)
        # Persistence diagrams (compute + save)
        self.persistence_analyzer.analyze(files, max_edge_length=self.max_edge_length)
        # Min–max block‑wise analysis (compute + save)
        self.minmax_analyzer.analyze(files, matrix_size=self.matrix_size)
        # Bottleneck and Wasserstein distances (compute + save)
        self.bottleneck_analyzer.analyze(
            files,
            persistence_analyzer=self.persistence_analyzer,
            delta=self.delta,
            order=self.order,
            save_path=self.save_path,
        )
        print("Pipeline finished successfully.")