"""
Module for AFM data analysis.

This module contains functions for computing autocorrelation functions,
calculating min/max indices for submatrices, and generating persistence diagrams
and barcodes from AFM datasets. It leverages libraries such as gudhi, matplotlib,
numpy, pandas, and statsmodels.
"""

import warnings

import gudhi
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import statsmodels.api as sm
from rich.progress import track

warnings.filterwarnings("ignore")


def plot_acf_graph(acf_df_x, acf_df_y, ax_x, ax_y):
    """
    Plot autocorrelation function graphs for x- and y-directions.

    Configures matplotlib settings, renames ACF columns, and plots the ACF curves.
    """
    plt.rc("font", size=12)  # Default text sizes
    plt.rc("axes", titlesize=17)  # Axes title size
    plt.rc("axes", labelsize=15)  # X and Y label size
    plt.rc("xtick", labelsize=15)  # Tick label size
    plt.rc("ytick", labelsize=15)  # Tick label size
    plt.rc("legend", fontsize=12)  # Legend size

    acf_df_x = acf_df_x.rename(columns={"ACF": "Along x-direction"})
    acf_df_y = acf_df_y.rename(columns={"ACF": "Along y-direction"})

    plt.figure(figsize=(7, 5))
    plt.plot("ix", "Along x-direction", data=acf_df_x, color="darkorange", linewidth=2.5)
    plt.plot("ix", "Along y-direction", data=acf_df_y, color="royalblue", linewidth=2.5)
    plt.axhline(y=0, xmin=0, xmax=1, linestyle="--", color="black")
    plt.axhline(y=0.1, xmin=0, xmax=1, linestyle="--", color="brown")
    plt.title(f"Autocorrelation along {ax_x}- and {ax_y}-direction")
    plt.legend()
    plt.xlabel("Sampling length, μm")
    plt.ylabel("Autocorrelation function, C(τ)")


def get_acf(df, nlags, series_no, constant, plot_acf=False):
    """
    Compute the autocorrelation function (ACF) for a series in a DataFrame.

    Extracts data for the x-direction from column "Pos = series_no" and for the y-direction
    from the transposed DataFrame. Returns a concatenated DataFrame with ACF values and
    scaled lag indices.
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
        plot_acf_graph(acf_df_x, acf_df_y, ax_x, ax_y)
    return acf_df


def autocorr_function(datasets, width_line):
    """
    Calculate and save autocorrelation functions for a list of datasets.

    For each dataset (CSV file path), reads the file into a DataFrame, computes the ACF
    using get_acf (with the series at the midpoint), and saves the ACF data as CSV and
    plots in PNG, SVG, and PDF formats.
    """
    for a in track(datasets, description="[green]Processing..."):
        df = pd.read_csv(a)
        acf_df = get_acf(
            df=df,
            nlags=int(len(df)),
            series_no=int(len(df) / 2),
            constant=width_line,
            plot_acf=True,
        )
        # Используем срез [:-4] для удаления ".csv"
        acf_df.to_csv(str(a)[:-4] + "_auto.csv")
        plt.savefig(
            str(a)[:-4] + "autocorr_function.png",
            format="png",
            dpi=1200,
            bbox_inches="tight",
        )
        plt.savefig(
            str(a)[:-4] + "autocorr_function.svg",
            format="svg",
            dpi=1200,
            bbox_inches="tight",
        )
        plt.savefig(
            str(a)[:-4] + "autocorr_function.pdf",
            format="pdf",
            dpi=1200,
            bbox_inches="tight",
        )


def persistance_db(datasets, max_edge_length):
    """
    Compute and save persistence diagrams and barcodes for a list of datasets using Gudhi.

    For each dataset (CSV file path), reads the data into a DataFrame, converts it to a NumPy
    array, constructs a Rips complex with the given max edge length, computes the persistence
    diagram, processes it into a DataFrame, saves the persistence data as CSV, and saves both a
    barcode and a persistence diagram in PNG, SVG, and PDF formats.
    """
    for a in track(datasets, description="[green]Processing..."):
        df = pd.read_csv(a)
        X = df.to_numpy()
        gudhi.persistence_graphical_tools._gudhi_matplotlib_use_tex = False
        rips_complex = gudhi.RipsComplex(distance_matrix=X, max_edge_length=max_edge_length)
        simplex_tree = rips_complex.create_simplex_tree(max_dimension=3)
        diag = simplex_tree.persistence(min_persistence=0)
        ans = extract_list_from_raw_data(diag)
        diag_df = pd.DataFrame(ans, columns=["Start", "End", "Length", "Homology group"])
        diag_df.to_csv(str(a)[:-4] + "diag_df_output.csv")
        gudhi.plot_persistence_barcode(
            diag,
            fontsize=18,
            legend=True,
            inf_delta=0.5,
            max_intervals=len(diag_df) + 1,
        )
        plt.xlabel("Sampling length, nm", fontsize=16)
        plt.ylabel("Topological invariants", fontsize=18)
        plt.xticks(fontsize=16)
        plt.yticks(fontsize=0)
        plt.savefig(
            str(a)[:-4] + "barcode.png",
            format="png",
            dpi=1200,
            bbox_inches="tight",
        )
        plt.savefig(
            str(a)[:-4] + "barcode.svg",
            format="svg",
            dpi=1200,
            bbox_inches="tight",
        )
        plt.savefig(
            str(a)[:-4] + "barcode.pdf",
            format="pdf",
            dpi=1200,
            bbox_inches="tight",
        )
        gudhi.plot_persistence_diagram(
            diag,
            fontsize=18,
            alpha=0.5,
            legend=True,
            inf_delta=0.2,
            greyblock=False,
            max_intervals=len(diag_df) + 1,
        )
        plt.xlabel("Feature appearance, nm", fontsize=18)
        plt.ylabel("Feature disappearance, nm", fontsize=18)
        plt.xticks(fontsize=16)
        plt.yticks(fontsize=16)
        plt.savefig(
            str(a)[:-4] + "persistence_diagram.png",
            format="png",
            dpi=1200,
            bbox_inches="tight",
        )
        plt.savefig(
            str(a)[:-4] + "persistence_diagram.svg",
            format="svg",
            dpi=1200,
            bbox_inches="tight",
        )
        plt.savefig(
            str(a)[:-4] + "persistence_diagram.pdf",
            format="pdf",
            dpi=1200,
            bbox_inches="tight",
        )


def return_min_max_ix(m):
    """
    Return the indices of the minimum and maximum elements in a matrix.

    Parameters
    ----------
    m : numpy.ndarray
        2D NumPy array.

    Returns
    -------
    list of int
        List containing four integers: [min_row, min_col, max_row, max_col].
    """
    min_ix = np.unravel_index(m.argmin(), m.shape)
    max_ix = np.unravel_index(m.argmax(), m.shape)
    return [min_ix[0], min_ix[1], max_ix[0], max_ix[1]]


def minmax_db(datasets):
    """
    Compute and save min/max indices for submatrices and flattened submatrices.

    For each dataset (CSV file path), reads data into a DataFrame indexed by "DataLine",
    converts it into a square matrix, divides it into 3x3 submatrices, computes min and max
    indices for each submatrix, aggregates the results, and saves two CSV files:
      - One with grouped min/max indices.
      - One with flattened submatrices.
    """
    for a in track(datasets, description="[green]Processing..."):
        data = pd.read_csv(a, index_col="DataLine")
        n = 3
        rows_to_drop = data.shape[0] - int(data.shape[0] / n) * n
        if rows_to_drop < 0:
            raise ValueError("Number of rows to drop cannot be negative.")
        if rows_to_drop == 0:
            mat = data.to_numpy()
        else:
            mat = data.iloc[:-rows_to_drop, :-rows_to_drop].to_numpy()
        if mat.shape[0] != mat.shape[1]:
            raise ValueError("Check the dimension of main square matrix.")
        if mat.shape[0] % n != 0:
            raise ValueError("Check the dimension of smaller square matrix.")
        i1 = 0
        i2 = n
        mat_list = []
        while i2 <= mat.shape[0]:
            j1 = 0
            j2 = n
            while j2 <= mat.shape[1]:
                mat_list.append(mat[i1:i2, j1:j2])
                j1 += n
                j2 += n
            i1 += n
            i2 += n

        sub_mat_df = pd.DataFrame(
            [x.flatten() for x in mat_list],
            columns=[f"ri_{i}_ci_{j}" for i in range(n) for j in range(n)],
        )

        min_max_ix_dict = {k + 1: return_min_max_ix(m) for k, m in enumerate(mat_list)}
        points = pd.DataFrame.from_dict(min_max_ix_dict).T.rename(
            columns={0: "min_r", 1: "min_c", 2: "max_r", 3: "max_c"}
        )
        min_df = points.groupby(["min_r", "min_c"]).size().reset_index()
        min_df = min_df.rename(columns={0: "X3", "min_r": "r", "min_c": "c"})
        min_df["type"] = "min"
        max_df = points.groupby(["max_r", "max_c"]).size().reset_index()
        max_df = max_df.rename(columns={0: "X3", "max_r": "r", "max_c": "c"})
        max_df["type"] = "max"
        points = pd.concat([min_df, max_df])
        points.to_csv(f"{a[:-4]}_min_max_ix({n}x{n}).csv", index=False)
        sub_mat_df.to_csv(f"{a[:-4]}_flattened_submat({n}x{n}).csv", index=False)


def extract_list_from_raw_data(diagrams):
    """
    Extract a structured list from raw persistence diagram data.

    Processes each persistence diagram tuple to extract:
      - Birth time (start value)
      - Death time (end value)
      - Persistence (absolute difference between start and end)
      - Homology group label

    Parameters
    ----------
    diagrams : list
        List of persistence diagram tuples, where each tuple is (homology group, (birth, death)).

    Returns
    -------
    list of list
        Each inner list contains: [birth, death, persistence, homology group].
    """
    ans = []
    for diagram in diagrams:
        ans.append(
            [
                diagram[1][0],
                diagram[1][1],
                abs(diagram[1][0] - diagram[1][1]),
                diagram[0],
            ]
        )
    return ans
