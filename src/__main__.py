"""
Main module for the AFM data processing pipeline.

This script orchestrates the analysis of Atomic Force Microscopy (AFM) data by
performing the following tasks:
  1. Prompting the user for image and analysis parameters.
  2. Converting text files containing matrix data to CSV files.
  3. Generating min/max index analysis on the CSV files.
  4. Calculating and plotting autocorrelation functions.
  5. Generating persistence barcodes and diagrams for topological analysis.

The processing steps rely on functions imported from various submodules:
  - src.AFM_analize_folder: Functions for autocorrelation, min/max analysis, and
    persistence diagrams.
  - src.convert: Function for converting matrix data to CSV format.
  - src.logic: Functions for folder selection and file listing.

User output is displayed using the Rich console with Markdown formatting.
"""

from rich.console import Console
from rich.markdown import Markdown

from src.AFM_analize_folder import autocorr_function, minmax_db, persistance_db
from src.convert import matrix_convert_save
from src.logic import folder_path, list_csv_files, list_txt_files


def main():
    """
    Execute the AFM data processing pipeline.

    This function performs the following steps:
      1. Initializes a Rich console for user interaction.
      2. Prompts the user to enter the line width (image length divided by the number
         of pixels) and the maximum edge length for the Rips complex.
      3. Selects the data folder and determines the output directory using
         `folder_path`.
      4. Lists text files in the selected folder using `list_txt_files` and converts them
         to CSV files via `matrix_convert_save`.
      5. Lists the resulting CSV files from the output directory using
         `list_csv_files`.
      6. Computes min/max indices of submatrices with `minmax_db`.
      7. Calculates and plots autocorrelation functions with `autocorr_function`.
      8. Generates persistence barcodes and diagrams with `persistance_db`.
      9. Displays Markdown-formatted messages to update the user on progress.

    Returns
    -------
    None
    """
    console = Console(record=False)
    console.print(Markdown("# Starting"))
    width_line = float(input("Enter line width (image length/number of pixels): "))
    max_edge_length = float(input("Enter max edge length for rips (default = 100): "))
    folder, save_path = folder_path()
    list_files_to_convert = list_txt_files(folder)
    console.print(Markdown("# Convering txt files"))
    matrix_convert_save(list_files_to_convert, save_path)
    list_of_csv_files = list_csv_files(save_path)
    console.print(Markdown("# Creating min/max"))
    minmax_db(list_of_csv_files)
    console.print(Markdown("# Creating autocorrelation fuction"))
    autocorr_function(list_of_csv_files, width_line)
    console.print(Markdown("# Creating barcodes and diagrams"))
    persistance_db(list_of_csv_files, max_edge_length)
    console.print(Markdown("# Finished!"))


if __name__ == "__main__":
    main()
