"""
Public API functions for AFM topological analysis.

These helper functions expose a simple interface for running parts of
the analysis pipeline programmatically.  They are intended for use in
contexts where the heavy computations need to be carried out on a
back‑end server and the results transmitted to a front‑end for
visualisation.  All functions return in‑memory pandas objects rather
than writing to disk, leaving it up to the caller to decide how to
persist or serialise the data.
"""

from __future__ import annotations

from typing import Dict, Iterable, List, Tuple

from afm_tda_tools.data.data import AnalysisData
from afm_tda_tools.analyzers.autocorrelation import AutocorrelationAnalyzer
from afm_tda_tools.analyzers.persistence import PersistenceAnalyzer
from afm_tda_tools.analyzers.min_max import MinMaxAnalyzer
from afm_tda_tools.analyzers.bottleneck import BottleneckAnalyzer


def run_acf(file_paths: Iterable[str], width_line: float = 0.1) -> Dict[str, object]:
    """
    Run autocorrelation analysis on a collection of CSV files.

    Parameters
    ----------
    file_paths : iterable of str
        Paths to CSV files to analyse.
    width_line : float, optional
        Sampling interval for lag scaling.  Default is ``0.1``.

    Returns
    -------
    dict
        Mapping of ``file_path`` to the resulting pandas DataFrame.  The
        DataFrame contains columns ``z``, ``ACF``, ``ix``, ``Series`` and
        ``Axis``.  No plots are generated or saved.
    """
    data_container = AnalysisData()
    analyzer = AutocorrelationAnalyzer(data_container)
    results: Dict[str, object] = {}
    for path in file_paths:
        results[path] = analyzer.compute(path, width_line)
    return results


def run_persistence(file_paths: Iterable[str], max_edge_length: float = 1.0) -> Dict[str, Tuple[list, object]]:
    """
    Run persistence homology analysis on a collection of CSV files.

    Parameters
    ----------
    file_paths : iterable of str
        Paths to CSV files containing distance matrices.
    max_edge_length : float, optional
        Maximum edge length for the Rips complex.  Default is ``1.0``.

    Returns
    -------
    dict
        Mapping of ``file_path`` to a tuple ``(diag, diag_df)`` where
        ``diag`` is the raw persistence diagram and ``diag_df`` is a
        pandas DataFrame describing the intervals.  No plots are
        generated or saved.
    """
    data_container = AnalysisData()
    analyzer = PersistenceAnalyzer(data_container)
    results: Dict[str, Tuple[list, object]] = {}
    for path in file_paths:
        diag, diag_df = analyzer.compute(path, max_edge_length)
        results[path] = (diag, diag_df)
    return results


def run_minmax(file_paths: Iterable[str], matrix_size: int = 3) -> Dict[str, Tuple[object, object]]:
    """
    Run min–max block‑wise analysis on a collection of CSV files.

    Parameters
    ----------
    file_paths : iterable of str
        Paths to CSV files containing square matrices with ``DataLine`` index.
    matrix_size : int, optional
        Block size for submatrices.  Default is ``3``.

    Returns
    -------
    dict
        Mapping of ``file_path`` to a tuple ``(agg_points, sub_mat_df)`` where
        ``agg_points`` is the aggregated counts DataFrame and ``sub_mat_df``
        is the DataFrame of flattened submatrices.
    """
    data_container = AnalysisData()
    analyzer = MinMaxAnalyzer(data_container)
    results: Dict[str, Tuple[object, object]] = {}
    for path in file_paths:
        agg_points, sub_mat_df = analyzer.compute(path, matrix_size)
        results[path] = (agg_points, sub_mat_df)
    return results


def run_bottleneck(
    file_paths: Iterable[str],
    diagrams: Dict[str, list] | None = None,
    delta: float = 0.01,
    order: float = 1.0,
    max_edge_length: float = 1.0,
) -> Tuple[object, object]:
    """
    Compute bottleneck and Wasserstein distance matrices for a collection
    of persistence diagrams.

    Parameters
    ----------
    file_paths : iterable of str
        Paths to CSV files containing distance matrices.  If ``diagrams``
        is provided, the files are used only as keys for naming the
        resulting matrices.
    diagrams : dict, optional
        Precomputed persistence diagrams keyed by file path.  If
        supplied, no new diagrams are computed.  If ``None``, diagrams
        are computed on the fly using ``max_edge_length``.
    delta : float, optional
        Tolerance parameter for the bottleneck distance.  Default is
        ``0.01``.
    order : float, optional
        Order parameter for the Wasserstein distance.  Default is
        ``1.0``.
    max_edge_length : float, optional
        Maximum edge length used when computing diagrams on the fly.
        Default is ``1.0``.

    Returns
    -------
    tuple
        ``(bn_df, ws_df)`` where ``bn_df`` and ``ws_df`` are pandas
        DataFrames containing bottleneck and Wasserstein distance matrices.
    """
    data_container = AnalysisData()
    analyzer = BottleneckAnalyzer(data_container)
    bn_df, ws_df = analyzer.compute(
        datasets=list(file_paths), diagrams=diagrams, delta=delta, order=order, max_edge_length=max_edge_length
    )
    return bn_df, ws_df