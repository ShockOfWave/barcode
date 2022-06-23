from code.logic import folder_path, list_txt_files, list_csv_files
from code.convert import matrix_convert_save
from code.AFM_analize_folder import minmax_db, autocorr_function, persistance_db

def main():
    folder, save_path = folder_path()
    list_files_to_convert = list_txt_files(folder)
    matrix_convert_save(list_files_to_convert, save_path)
    list_of_csv_files = list_csv_files(save_path)
    minmax_db(list_of_csv_files)
    autocorr_function(list_of_csv_files)
    persistance_db(list_of_csv_files)

if __name__ == '__main__':
    main()