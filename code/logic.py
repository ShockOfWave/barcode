from simple_term_menu import TerminalMenu
import os
from pathlib import Path

def get_project_path():
    path = Path(__file__).parent.parent
    return path

def folder_path():
    path_to_folders = []
    for root, dirs, files in os.walk(get_project_path()):
        for dir in dirs:
            path_to_folders.append(os.path.join(root, dir))
    exeptions = []
    for path in path_to_folders:
        if 'code' in path.split(os.sep):
            exeptions.append(path)
        elif 'Code' in path.split(os.sep):
            exeptions.append(path)
        elif '.idea' in path.split(os.sep):
            exeptions.append(path)
        elif '.git' in path.split(os.sep):
            exeptions.append(path)
    options = [i for i in path_to_folders if i not in exeptions]
    terminal_menu = TerminalMenu(options)
    menu_entry_index = terminal_menu.show()
    folder = options[menu_entry_index]
    save_path = os.path.join(folder, 'output')
    return folder, save_path

def list_txt_files(folder):
    list_txt_files = []
    for root, dirs, files in os.walk(folder):
        for file in files:
            if file.endswith('.txt'):
                list_txt_files.append(os.path.join(root, file))

    return list_txt_files

def list_csv_files(folder):
    list_csv_files = []
    for root, dirs, files in os.walk(folder):
        for file in files:
            if file.endswith('csv'):
                list_csv_files.append(os.path.join(root, file))
    return list_csv_files
