import numpy as np

def matrix_convert_save(dataset):
    for file in dataset:
        filik=open(file,"r")
        listik=[]
        for line in filik:
            stripped_line=line.strip()
            line_list=stripped_line.split()
            listik.append(line_list)
        dfs=listik[4:]
        dflength=len(dfs)
        first_line=['DataLine']
        for i in range(dflength):
            first_line.append('Pos = '+str(i))
        dfs_new=[[float(item)*10**9 for item in list] for list in dfs]
        j=0
        for line in dfs_new:
            line.insert(0,j)
            j=j+1
        dfs_new.insert(0,first_line)
        np.savetxt(file[:-4]+".csv",dfs_new ,fmt='%s', delimiter=",")
        print(f'Successfully converted ------- {file}')
        



