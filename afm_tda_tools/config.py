"""
Module for centralized Matplotlib styling configuration.

This module defines `MatplotlibConfig`, a simple utility to set
consistent font and label sizes across all Matplotlib plots.
"""

import matplotlib.pyplot as plt


class MatplotlibConfig:
    """
    Configuration for Matplotlib plot aesthetics.

    Provides default size settings for fonts, axis titles, axis labels,
    tick labels, and legend text, and applies them to Matplotlib rcParams.

    Attributes
    ----------
    font_size : int
        Base font size for plot text.
    axes_title_size : int
        Font size for axis titles.
    axes_label_size : int
        Font size for axis labels.
    tick_label_size : int
        Font size for tick labels on both axes.
    legend_size : int
        Font size for legend text.
    """

    def __init__(self):
        """
        Initialize default plot size parameters.

        Sets sensible defaults for fonts, titles, labels, ticks, and legends.
        """
        self.font_size = 12
        self.axes_title_size = 17
        self.axes_label_size = 15
        self.tick_label_size = 15
        self.legend_size = 12

    def apply(self):
        """
        Apply the configured sizes to Matplotlib rcParams.

        Modifies the following rcParams keys:
        - "font.size"
        - "axes.titlesize"
        - "axes.labelsize"
        - "xtick.labelsize"
        - "ytick.labelsize"
        - "legend.fontsize"
        """
        plt.rc("font", size=self.font_size)
        plt.rc("axes", titlesize=self.axes_title_size)
        plt.rc("axes", labelsize=self.axes_label_size)
        plt.rc("xtick", labelsize=self.tick_label_size)
        plt.rc("ytick", labelsize=self.tick_label_size)
        plt.rc("legend", fontsize=self.legend_size)
