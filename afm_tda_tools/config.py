"""
Centralised Matplotlib styling configuration.

The class :class:`MatplotlibConfig` encapsulates default font sizes and
applies them to Matplotlib's rcParams.  This is preserved from the
original project to ensure consistent aesthetics across plots.
"""

from __future__ import annotations

import matplotlib.pyplot as plt


class MatplotlibConfig:
    """
    Configuration for Matplotlib plot aesthetics.

    Provides default size settings for fonts, axis titles, axis labels,
    tick labels and legend text, and applies them to Matplotlib rcParams.
    """

    def __init__(self) -> None:
        self.font_size = 12
        self.axes_title_size = 17
        self.axes_label_size = 15
        self.tick_label_size = 15
        self.legend_size = 12

    def apply(self) -> None:
        """Apply the configured sizes to Matplotlib rcParams."""
        plt.rc("font", size=self.font_size)
        plt.rc("axes", titlesize=self.axes_title_size)
        plt.rc("axes", labelsize=self.axes_label_size)
        plt.rc("xtick", labelsize=self.tick_label_size)
        plt.rc("ytick", labelsize=self.tick_label_size)
        plt.rc("legend", fontsize=self.legend_size)