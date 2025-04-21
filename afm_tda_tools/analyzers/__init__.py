"""
Subpackage defining AFM data analysis routines.

This module aggregates the primary Analyzer classes used in the
pipeline for various computational tasks on AFM datasets.

Classes
-------
AutocorrelationAnalyzer
    Computes and saves autocorrelation functions for CSV datasets.
PersistenceAnalyzer
    Computes persistence homology diagrams and plots from point-cloud data.
MinMaxAnalyzer
    Identifies and aggregates local minima and maxima in matrix blocks.
BottleneckAnalyzer
    Computes pairwise bottleneck and Wasserstein distances between persistence diagrams.
"""

from .autocorrelation import AutocorrelationAnalyzer
from .bottleneck import BottleneckAnalyzer
from .min_max import MinMaxAnalyzer
from .persistence import PersistenceAnalyzer

__all__ = [
    "AutocorrelationAnalyzer",
    "PersistenceAnalyzer",
    "MinMaxAnalyzer",
    "BottleneckAnalyzer",
]
