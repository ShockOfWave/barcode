from src.logic import folder_path, list_txt_files, list_csv_files
from src.convert import matrix_convert_save
from src.AFM_analize_folder import minmax_db, autocorr_function, persistance_db

from rich.console import Console
from rich.markdown import Markdown

def main():
    console = Console(record=False)
    console.print(Markdown("# Starting"))
    width_line = float(input('Enter line width (image length/number of pixels): '))
    max_edge_length = float(input('Enter max edge length for rips (default = 100): '))
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

if __name__ == '__main__':
    main()
