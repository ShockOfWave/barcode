"""
Module for file and folder operations in the AFM data analysis pipeline.

This module contains functions for selecting data folders, listing files with
specific extensions, and utilities for handling file paths used throughout the
data processing pipeline.
"""

import json
import os
from pathlib import Path

from simple_term_menu import TerminalMenu


def get_project_path():
    """
    Get the root directory of the project.

    Returns
    -------
    Path
        A pathlib.Path object pointing to the root directory of the project.
    """
    path = Path(__file__).parent.parent
    return path


def load_excluded_dirs(config_file="config.json"):
    """
    Load the list of directories to exclude from the given JSON config file.

    Parameters
    ----------
    config_file : str
        Path to the configuration file (default is 'config.json').

    Returns
    -------
    list of str
        List of directory names to be excluded.
    """
    try:
        with open(os.path.join(get_project_path(), "src", config_file)) as f:
            config = json.load(f)
        return config.get("excluded_dirs", [])
    except Exception:
        # Fallback to default list if file reading fails
        return ["src", ".idea", ".git", "venv"]


def folder_path():
    """
    Prompt the user to select a data folder and determine an output folder.

    Traverses the project directory, excluding directories loaded from the config file,
    then presents a terminal menu for folder selection. The output folder is assumed to be
    a subdirectory named "output" within the selected folder.

    Returns
    -------
    tuple of (str, str)
        Selected folder path and its "output" subdirectory path.
    """
    excluded_dirs = load_excluded_dirs()
    path_to_folders = []
    for root, dirs, _ in os.walk(get_project_path()):
        for dir_name in dirs:
            path_to_folders.append(os.path.join(root, dir_name))
    exceptions = []
    for path in path_to_folders:
        if any(exc in path.split(os.sep) for exc in excluded_dirs):
            exceptions.append(path)
    options = [i for i in path_to_folders if i not in exceptions]
    terminal_menu = TerminalMenu(options)
    menu_entry_index = terminal_menu.show()
    folder = options[menu_entry_index]
    save_path = os.path.join(folder, "output")
    return folder, save_path


def list_txt_files(folder):
    """
    Create a list of all .txt files in the given folder.

    The function recursively walks through the specified folder and its subdirectories,
    collecting paths to files that end with the ".txt" extension.

    Parameters
    ----------
    folder : str
        The path to the folder where the search for .txt files will be performed.

    Returns
    -------
    list of str
        A list of full paths to the .txt files found in the folder.
    """
    list_txt_files = []
    for root, _dirs, files in os.walk(folder):
        for file in files:
            if file.endswith(".txt"):
                list_txt_files.append(os.path.join(root, file))

    return list_txt_files


def list_csv_files(folder):
    """
    Create a list of all .csv files in the given folder.

    The function recursively walks through the specified folder and its subdirectories,
    collecting paths to files that end with the ".csv" extension.

    Parameters
    ----------
    folder : str
        The path to the folder where the search for .csv files will be performed.

    Returns
    -------
    list of str
        A list of full paths to the .csv files found in the folder.
    """
    list_csv_files = []
    for root, _dirs, files in os.walk(folder):
        for file in files:
            if file.endswith("csv"):
                list_csv_files.append(os.path.join(root, file))
    return list_csv_files
