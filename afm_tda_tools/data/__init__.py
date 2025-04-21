"""
Package for AFM data handling and preprocessing utilities.

This submodule provides core data structures and conversion functions
for reading raw AFM `.txt` files, storing intermediate analysis results,
and exposing a unified interface.

Exports
-------
AnalysisData
    Container class for storing and retrieving analysis outputs.
txt_to_csv_folder
    Function to convert raw `.txt` files into structured CSV files.
"""

from .data import AnalysisData
from .data_converter import txt_to_csv_folder

__all__ = ["AnalysisData", "txt_to_csv_folder"]
