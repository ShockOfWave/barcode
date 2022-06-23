import numpy as np
import os

def matrix_convert_save(dataset, save_path):
    for file in dataset:
        filik = open(file, "r")
        listik = []
        for line in filik:
            stripped_line = line.strip()
            line_list = stripped_line.split()
            listik.append(line_list)
        dfs = listik[4:]
        dflength = len(dfs)
        first_line = ['DataLine']
        for i in range(dflength):
            first_line.append('Pos = '+str(i))
        dfs_new = [[float(item)*10**9 for item in list] for list in dfs]
        j = 0
        for line in dfs_new:
            line.insert(0, j)
            j = j+1
        dfs_new.insert(0, first_line)
        file_name = file.split(os.sep)[-1][:-4]
        if os.path.exists(save_path):
            pass
        else:
            os.mkdir(save_path)
        if os.path.exists(os.path.join(save_path, file_name)):
            pass
        else:
            os.mkdir(os.path.join(save_path, file_name))
        np.savetxt(os.path.join(save_path, file_name, (file_name + '.csv')), dfs_new, fmt='%s', delimiter=',')
        print(f'Successfully converted ------- {file}')



