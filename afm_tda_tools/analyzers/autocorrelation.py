"""
Module for autocorrelation analysis.

This module defines the `AutocorrelationAnalyzer` class, which computes
and saves autocorrelation functions along the x and y directions for
given CSV datasets.
"""

import os

import matplotlib.pyplot as plt
import pandas as pd
import statsmodels.api as sm
from rich.progress import track

from .base import Analyzer


class AutocorrelationAnalyzer(Analyzer):
    """
    Analyzer for computing autocorrelation functions on CSV datasets.

    This analyzer reads each CSV file, computes the autocorrelation along
    the middle series in both x and y directions, and saves both the
    numeric results and plots.

    Parameters
    ----------
    data_container : AnalysisData, optional
        Container for storing analysis outputs. If `None`, a new
        `AnalysisData` instance is created.
    """

    def __init__(self, data_container=None):
        super().__init__(data_container)

    def analyze(self, datasets, width_line):
        """
        Compute and save autocorrelation for each dataset.

        For each CSV file in `datasets`, reads the data into a DataFrame,
        computes the autocorrelation function along the central series in
        both x and y directions using a lag increment of `width_line`,
        stores the results in the shared data container, and persists
        both CSV and figure outputs.

        Parameters
        ----------
        datasets : list of str
            Paths to CSV files to analyze.
        width_line : float
            Sampling interval (in micrometers) used to scale the lag axis.

        Returns
        -------
        None
        """
        for file_path in track(datasets, description="[green]Processing autocorrelation..."):
            df = pd.read_csv(file_path)
            acf_df = self._get_acf(
                df=df,
                nlags=int(len(df)),
                series_no=int(len(df) / 2),
                constant=width_line,
                plot_acf=True,
            )
            self.data.add_acf_data(file_path, acf_df)
            self._save_acf_data(file_path, acf_df)

    def _plot_acf_graph(self, acf_df_x, acf_df_y, ax_x, ax_y):
        """
        Plot the autocorrelation functions along x and y directions.

        Applies Matplotlib configuration, draws both curves on the same
        axes, and stylizes the plot with lines, titles, and labels.

        Parameters
        ----------
        acf_df_x : pandas.DataFrame
            DataFrame containing autocorrelation values for the x-direction.
        acf_df_y : pandas.DataFrame
            DataFrame containing autocorrelation values for the y-direction.
        ax_x : str
            Label for the x-axis series (e.g., "x").
        ax_y : str
            Label for the y-axis series (e.g., "y").

        Returns
        -------
        None
        """
        self.plt_config.apply()

        acf_df_x = acf_df_x.rename(columns={"ACF": "Along x-direction"})
        acf_df_y = acf_df_y.rename(columns={"ACF": "Along y-direction"})

        plt.figure(figsize=(7, 5))
        plt.plot(
            "ix",
            "Along x-direction",
            data=acf_df_x,
            color="darkorange",
            linewidth=2.5,
        )
        plt.plot(
            "ix",
            "Along y-direction",
            data=acf_df_y,
            color="royalblue",
            linewidth=2.5,
        )
        plt.axhline(y=0, xmin=0, xmax=1, linestyle="--", color="black")
        plt.axhline(y=0.1, xmin=0, xmax=1, linestyle="--", color="brown")
        plt.title(f"Autocorrelation along {ax_x}- and {ax_y}-direction")
        plt.legend()
        plt.xlabel("Sampling length, μm")
        plt.ylabel("Autocorrelation function, C(τ)")

    def _get_acf(self, df, nlags, series_no, constant, plot_acf=False):
        """
        Compute the autocorrelation function for x and y series.

        Extracts the central series from the DataFrame in both the
        horizontal (x) and vertical (y) directions, computes the
        autocorrelation up to `nlags`, and optionally plots the results.

        Parameters
        ----------
        df : pandas.DataFrame
            DataFrame containing columns "DataLine" and "Pos = i" series.
        nlags : int
            Number of lags to compute in the autocorrelation.
        series_no : int
            Index of the series (column) around which to compute autocorrelation.
        constant : float
            Sampling interval multiplier for the lag axis.
        plot_acf : bool, default False
            If `True`, a plot of the autocorrelation is generated.

        Returns
        -------
        pandas.DataFrame
            Concatenated DataFrame with columns:
            - "z": original values,
            - "ACF": autocorrelation values,
            - "ix": lag distances scaled by `constant`,
            - "Series": series index,
            - "Axis": 'x' or 'y'.
        """
        val_x = df[f"Pos = {series_no}"].values
        ax_x = "x"

        val_y = df.set_index("DataLine").T.iloc[:, series_no].values
        ax_y = "y"

        auto_corr_x = sm.tsa.stattools.acf(val_x, nlags=nlags, qstat=False, alpha=None)
        auto_corr_y = sm.tsa.stattools.acf(val_y, nlags=nlags, qstat=False, alpha=None)

        acf_df_x = pd.DataFrame(
            {
                "z": val_x,
                "ACF": auto_corr_x,
                "ix": [i * constant for i in range(len(auto_corr_x))],
                "Series": [series_no] * len(auto_corr_x),
                "Axis": [ax_x] * len(auto_corr_x),
            }
        )
        acf_df_y = pd.DataFrame(
            {
                "z": val_y,
                "ACF": auto_corr_y,
                "ix": [i * constant for i in range(len(auto_corr_y))],
                "Series": [series_no] * len(auto_corr_y),
                "Axis": [ax_y] * len(auto_corr_y),
            }
        )

        acf_df = pd.concat([acf_df_x, acf_df_y])

        if plot_acf:
            self._plot_acf_graph(acf_df_x, acf_df_y, ax_x, ax_y)
        return acf_df

    def _save_acf_data(self, file_path, acf_df):
        """
        Save autocorrelation results and plots to files.

        Writes the autocorrelation DataFrame to CSV and saves the figure
        in PNG, SVG, and PDF formats with high resolution.

        Parameters
        ----------
        file_path : str
            Original CSV file path (without extension handling).
        acf_df : pandas.DataFrame
            DataFrame containing autocorrelation results.

        Returns
        -------
        None
        """
        base_path = os.path.dirname(file_path)
        acf_df.to_csv(os.path.join(base_path, "autocorr.csv"))
        plt.savefig(
            os.path.join(base_path, "autocorr_function.png"),
            format="png",
            dpi=1200,
            bbox_inches="tight",
        )
        plt.savefig(
            os.path.join(base_path, "autocorr_function.svg"),
            format="svg",
            dpi=1200,
            bbox_inches="tight",
        )
        plt.savefig(
            os.path.join(base_path, "autocorr_function.pdf"),
            format="pdf",
            dpi=1200,
            bbox_inches="tight",
        )
