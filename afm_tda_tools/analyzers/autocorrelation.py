"""
Autocorrelation analysis tools.

This module defines the :class:`AutocorrelationAnalyzer` class, which
computes and optionally plots autocorrelation functions for each CSV
dataset.  The class separates the heavy numerical computation from
plotting and file I/O.  In contrast to the original implementation
where computation and plotting were tightly coupled and always wrote
files to disk, the methods here follow a compute/plot/save pattern:

* :meth:`compute` returns a pandas DataFrame containing the raw
  autocorrelation values without producing any plots.
* :meth:`plot_acf` accepts the DataFrame and returns a Matplotlib
  figure; this can be called by a client (e.g. a web frontend) to
  display the graph.
* :meth:`save_results` writes both the DataFrame and optional plot
  to disk.

This design allows the analysis to be used in CLI scripts as well as
inside larger applications where results may be serialised and sent to a
frontend for visualisation.
"""

from __future__ import annotations

import os

import matplotlib.pyplot as plt
import pandas as pd
import statsmodels.api as sm
from rich.progress import track

from .base import Analyzer


def _convert_data_to_expected_format(df: pd.DataFrame) -> pd.DataFrame:
    """
    Преобразует матрицу данных в формат, ожидаемый анализатором.

    Parameters
    ----------
    df : pd.DataFrame
        Исходная матрица данных

    Returns
    -------
    pd.DataFrame
        DataFrame с колонками DataLine и Pos = i
    """
    if "DataLine" in df.columns and any(col.startswith("Pos = ") for col in df.columns):
        return df

    rows, cols = df.shape
    data = {f"Pos = {i}": df.iloc[:, i].to_numpy() for i in range(cols)}
    data["DataLine"] = range(rows)
    column_order = ["DataLine", *[f"Pos = {i}" for i in range(cols)]]
    return pd.DataFrame(data, columns=column_order)


class AutocorrelationAnalyzer(Analyzer):
    """
    Autocorrelation function analyzer for AFM data.

    This analyzer computes the autocorrelation function (ACF) for AFM height
    data in both x and y directions.  It extracts the central series from
    the data matrix and computes the autocorrelation using the statsmodels
    library.

    The ACF is useful for characterizing the spatial correlation structure
    of surface roughness and can help identify characteristic length scales
    in the data.

    Attributes
    ----------
    data : object, optional
        Shared data container for storing results.
    plt_config : object
        Matplotlib configuration object for consistent plotting.
    """

    def __init__(self, data_container: object | None = None) -> None:
        super().__init__(data_container)

    def compute(self, file_path: str, width_line: float) -> pd.DataFrame:
        """
        Compute the autocorrelation for a single dataset.

        Parameters
        ----------
        file_path : str
            Path to the CSV or TXT file to analyze.
        width_line : float
            Sampling interval (in micrometres) used to scale the lag axis.

        Returns
        -------
        pandas.DataFrame
            DataFrame containing columns ``z``, ``ACF``, ``ix``, ``Series``
            and ``Axis`` for both x and y directions.
        """
        # Определяем формат файла и читаем данные
        if file_path.endswith('.txt'):
            # Для .txt файлов читаем как матрицу
            try:
                # Пропускаем комментарии и читаем данные
                data = []
                with open(file_path) as f:
                    for line in f:
                        line = line.strip()
                        if line and not line.startswith('#'):
                            # Разбиваем по табуляции или пробелам
                            values = line.split()
                            if values:
                                data.append([float(v) for v in values])
                
                if not data:
                    raise ValueError("No valid data found in file")
                
                df = pd.DataFrame(data)
            except Exception as e:
                raise ValueError(f"Error reading TXT file: {e}") from e
        else:
            # Для CSV файлов используем стандартное чтение
            df = pd.read_csv(file_path)
        
        # Преобразуем данные в нужный формат
        df = _convert_data_to_expected_format(df)
        
        # determine central series
        nlags = int(len(df))
        series_no = int(len(df) / 2)
        acf_df = self._get_acf(
            df=df,
            nlags=nlags,
            series_no=series_no,
            constant=width_line,
            plot_acf=False,
        )
        # store result in shared container
        if hasattr(self, 'data') and self.data is not None:
            self.data.add_acf_data(file_path, acf_df)
        return acf_df

    # -- high level API for CLI -------------------------------------------
    def analyze(self, datasets: list[str], width_line: float) -> None:
        """
        Compute and save autocorrelation for each dataset.

        This method iterates over each CSV file in ``datasets``, computes
        the autocorrelation, stores it in the shared data container and
        writes both the DataFrame and the plot to disk.  It is designed
        for the CLI use case where saving results is desirable.

        Parameters
        ----------
        datasets : list of str
            Paths to CSV files to analyse.
        width_line : float
            Sampling interval (in micrometres) used to scale the lag axis.
        """
        for file_path in track(datasets, description="[green]Processing autocorrelation..."):
            acf_df = self.compute(file_path, width_line)
            # Save DataFrame and plot
            self.save_results(file_path, acf_df)

    # -- save --------------------------------------------------------------
    def save_results(self, file_path: str, acf_df: pd.DataFrame, save_plot: bool = True) -> None:
        """
        Persist autocorrelation results to disk.

        Writes the provided DataFrame to ``autocorr.csv`` in the same
        directory as the input file.  If ``save_plot`` is ``True`` a
        plot is generated via :meth:`plot_acf` and saved in PNG, SVG and
        PDF formats.

        Parameters
        ----------
        file_path : str
            Original CSV file path.
        acf_df : pandas.DataFrame
            DataFrame containing autocorrelation results.
        save_plot : bool, optional
            Whether to generate and save plots.  Default is ``True``.
        """
        base_path = os.path.dirname(file_path)
        # Save the data to CSV
        acf_df.to_csv(os.path.join(base_path, "autocorr.csv"), index=False)
        # Optionally create and save plots
        if save_plot:
            fig = self.plot_acf(acf_df)
            for ext in ("png", "svg", "pdf"):
                fig.savefig(
                    os.path.join(base_path, f"autocorr_function.{ext}"),
                    format=ext,
                    dpi=1200,
                    bbox_inches="tight",
                )
            plt.close(fig)

    # -- plot --------------------------------------------------------------
    def plot_acf(self, acf_df: pd.DataFrame, ax_x: str = "x", ax_y: str = "y"):
        """
        Create a Matplotlib figure for the autocorrelation functions.

        Parameters
        ----------
        acf_df : pandas.DataFrame
            DataFrame returned from :meth:`compute` containing ACF values.
        ax_x : str, optional
            Label for the x‑axis series.  Default is ``"x"``.
        ax_y : str, optional
            Label for the y‑axis series.  Default is ``"y"``.

        Returns
        -------
        matplotlib.figure.Figure
            A figure object with the autocorrelation plot.  The caller is
            responsible for closing it.
        """
        # Apply global styling
        self.plt_config.apply()
        # Split the DataFrame into x and y components
        acf_df_x = acf_df[acf_df["Axis"] == ax_x].rename(columns={"ACF": f"Along {ax_x}-direction"})
        acf_df_y = acf_df[acf_df["Axis"] == ax_y].rename(columns={"ACF": f"Along {ax_y}-direction"})

        fig, ax = plt.subplots(figsize=(7, 5))
        if not acf_df_x.empty:
            ax.plot(
                acf_df_x["ix"],
                acf_df_x[f"Along {ax_x}-direction"],
                color="darkorange",
                linewidth=2.5,
                label=f"Along {ax_x}-direction",
            )
        if not acf_df_y.empty:
            ax.plot(
                acf_df_y["ix"],
                acf_df_y[f"Along {ax_y}-direction"],
                color="royalblue",
                linewidth=2.5,
                label=f"Along {ax_y}-direction",
            )
        ax.axhline(y=0, xmin=0, xmax=1, linestyle="--", color="black")
        ax.axhline(y=0.1, xmin=0, xmax=1, linestyle="--", color="brown")
        ax.set_title(f"Autocorrelation along {ax_x}- and {ax_y}-direction")
        ax.set_xlabel("Sampling length, μm")
        ax.set_ylabel("Autocorrelation function, C(τ)")
        
        # Добавляем легенду только если есть помеченные линии
        handles, labels = ax.get_legend_handles_labels()
        if handles:
            ax.legend()
        
        return fig

    # -- internal helper ---------------------------------------------------
    def _get_acf(
        self, df: pd.DataFrame, nlags: int, series_no: int, constant: float, plot_acf: bool = False
    ) -> pd.DataFrame:
        """
        Compute the autocorrelation function for x and y series.

        This helper extracts the central series from the DataFrame in both
        the horizontal (x) and vertical (y) directions, computes the
        autocorrelation up to ``nlags`` and returns a concatenated
        DataFrame.  If ``plot_acf`` is ``True`` a plot is generated via
        :meth:`plot_acf`.

        Parameters
        ----------
        df : pandas.DataFrame
            DataFrame containing columns ``DataLine`` and ``Pos = i`` series.
        nlags : int
            Number of lags to compute in the autocorrelation.
        series_no : int
            Index of the series (column) around which to compute autocorrelation.
        constant : float
            Sampling interval multiplier for the lag axis.
        plot_acf : bool, optional
            If ``True`` a plot of the autocorrelation is generated.

        Returns
        -------
        pandas.DataFrame
            Concatenated DataFrame with columns:
            ``z`` (original values), ``ACF`` (autocorrelation values),
            ``ix`` (lag distances scaled by ``constant``), ``Series`` and
            ``Axis``.
        """
        # extract x direction
        val_x = df[f"Pos = {series_no}"].values
        ax_x = "x"
        # extract y direction
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

        acf_df = pd.concat([acf_df_x, acf_df_y], ignore_index=True)

        if plot_acf:
            # generate and save figure but do not return it here
            fig = self.plot_acf(acf_df)
            plt.close(fig)
        return acf_df