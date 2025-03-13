"""
Tests for the logic module of the Barcode project.

This module tests functions from src.logic:
    - folder_path
    - list_csv_files
    - list_txt_files
    - load_excluded_dirs

It uses temporary directories and config files created via pytest fixtures.
"""

import json
import os
import shutil

import pytest
from simple_term_menu import TerminalMenu

from src.logic import (
    folder_path,
    list_csv_files,
    list_txt_files,
    load_excluded_dirs,
)


@pytest.fixture
def temp_dir(tmp_path):
    """
    Create a temporary directory with a specific structure for testing.

    The structure includes:
      - A 'data' directory containing a file 'file.txt'
      - A 'src' directory
      - A '.git' directory

    Parameters
    ----------
    tmp_path : pathlib.Path
        Temporary directory provided by pytest.

    Returns
    -------
    pathlib.Path
        The temporary directory with the created structure.
    """
    data_dir = tmp_path / "data"
    data_dir.mkdir()
    (data_dir / "file.txt").write_text("sample text")
    (tmp_path / "src").mkdir()
    (tmp_path / ".git").mkdir()
    return tmp_path


@pytest.fixture
def temp_config(tmp_path):
    """
    Create a temporary JSON configuration file with excluded directories.

    The configuration file contains:
        {"excluded_dirs": ["src", ".git"]}

    Parameters
    ----------
    tmp_path : pathlib.Path
        Temporary directory provided by pytest.

    Returns
    -------
    pathlib.Path
        The file path to the created configuration file.
    """
    config = {"excluded_dirs": ["src", ".git"]}
    config_file = tmp_path / "config.json"
    config_file.write_text(json.dumps(config))
    return config_file


def test_load_excluded_dirs(temp_config, monkeypatch):
    """
    Test the load_excluded_dirs function.

    Changes the current directory to the configuration file's parent,
    loads the excluded directories from the config file, and asserts that
    the result is a list containing "src" and ".git".

    Parameters
    ----------
    temp_config : pathlib.Path
        Temporary configuration file fixture.
    monkeypatch : pytest.MonkeyPatch
        Monkeypatch fixture for modifying environment.
    """
    monkeypatch.chdir(temp_config.parent)
    excluded = load_excluded_dirs(str(temp_config))
    assert isinstance(excluded, list)
    assert "src" in excluded
    assert ".git" in excluded


def test_list_txt_files(tmp_path):
    """
    Test the list_txt_files function.

    Creates a temporary 'data' directory with one .txt file and one .csv file,
    then asserts that only the .txt file is returned.

    Parameters
    ----------
    tmp_path : pathlib.Path
        Temporary directory provided by pytest.
    """
    data_dir = tmp_path / "data"
    data_dir.mkdir()
    file1 = data_dir / "a.txt"
    file2 = data_dir / "b.csv"
    file1.write_text("text")
    file2.write_text("csv")
    txt_files = list_txt_files(str(tmp_path))
    assert str(file1) in txt_files
    assert str(file2) not in txt_files


def test_list_csv_files(tmp_path):
    """
    Test the list_csv_files function.

    Creates a temporary 'data' directory with one .csv file and one .txt file,
    then asserts that only the .csv file is returned.

    Parameters
    ----------
    tmp_path : pathlib.Path
        Temporary directory provided by pytest.
    """
    data_dir = tmp_path / "data"
    data_dir.mkdir()
    file1 = data_dir / "a.csv"
    file2 = data_dir / "b.txt"
    file1.write_text("csv")
    file2.write_text("text")
    csv_files = list_csv_files(str(tmp_path))
    assert str(file1) in csv_files
    assert str(file2) not in csv_files


def test_folder_path(temp_dir, monkeypatch):
    """
    Test the folder_path function.

    Overrides the get_project_path function to return temp_dir and
    forces the TerminalMenu.show method to always return 0. Asserts that the
    returned folder path does not contain excluded directories and that the
    save_path ends with "output".

    Parameters
    ----------
    temp_dir : pathlib.Path
        Temporary directory fixture with a predefined structure.
    monkeypatch : pytest.MonkeyPatch
        Monkeypatch fixture for modifying behavior.
    """
    monkeypatch.setattr("src.logic.get_project_path", lambda: temp_dir)
    monkeypatch.setattr(TerminalMenu, "show", lambda self: 0)
    folder, save_path = folder_path()
    assert "src" not in folder and ".git" not in folder
    assert save_path.endswith("output")
    if os.path.exists(save_path):
        shutil.rmtree(save_path)
