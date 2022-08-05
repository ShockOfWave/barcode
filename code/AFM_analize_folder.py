#Autocorrelation function
#Persistance diagram
#Barcode diagram
#min_max

import numpy as np
import pandas as pd
from ripser import Rips
import matplotlib.pyplot as plt
import gudhi
import statsmodels.tsa.api as smt
import statsmodels
import warnings
import os
from code.Save_barcode_as_csv_2 import extract_list_from_raw_data
warnings.filterwarnings('ignore')

def plot_acf_graph(acf_df_x, acf_df_y, ax_x, ax_y):
    
    plt.rc('font', size = 12)          # controls default text sizes
    plt.rc('axes', titlesize = 17)     # fontsize of the axes title
    plt.rc('axes', labelsize = 15)    # fontsize of the x and y labels
    plt.rc('xtick', labelsize = 15)    # fontsize of the tick labels
    plt.rc('ytick', labelsize = 15)    # fontsize of the tick labels
    plt.rc('legend', fontsize = 12)    # legend fontsize
    
    acf_df_x = acf_df_x.rename(columns = {'ACF' : 'Along x-direction'})
    acf_df_y = acf_df_y.rename(columns = {'ACF' : 'Along y-direction'})

    #acf_df[['ACF']].plot(linewidth = 2.5, figsize = (8, 5), legend = False)
    plt.figure(figsize = (7, 5))
    plt.plot('ix', 'Along x-direction', data = acf_df_x, color = 'darkorange', linewidth = 2.5,)
    plt.plot('ix', 'Along y-direction', data = acf_df_y, color = 'royalblue', linewidth = 2.5,)
    plt.axhline(y = 0, xmin = 0, xmax = 1, linestyle = '--', color = 'black');
    plt.axhline(y = 0.1, xmin = 0, xmax = 1, linestyle = '--', color = 'brown');
    plt.title(f"Autocorrelation along {ax_x}- and {ax_y}-direction")
    plt.legend()
    plt.xlabel('Sampling length, μm')
    plt.ylabel('Autocorrelation function, C(τ)');

def get_acf(df, nlags, series_no, constant, plot_acf = False):

    val_x = df[f'Pos = {series_no}'].values
    ax_x = 'x'

    val_y = df.set_index('DataLine').T.iloc[:, series_no].values
    ax_y = 'y'
    
    auto_corr_x = statsmodels.tsa.stattools.acf(val_x,  
                                              nlags = nlags, qstat = False, 
                                              alpha = None,)
    auto_corr_y = statsmodels.tsa.stattools.acf(val_y,  
                                              nlags = nlags, qstat = False, 
                                              alpha = None,)
    
    acf_df_x = pd.DataFrame({'z' : val_x, 
                           'ACF' : auto_corr_x, 
                           'ix' : [i * constant for i in range(0, len(auto_corr_x))],
                           'Series' : [series_no] * len(auto_corr_x),
                           'Axis' : [ax_x] * len(auto_corr_x)})
    
    acf_df_y = pd.DataFrame({'z' : val_y, 
                           'ACF' : auto_corr_y, 
                           'ix' : [i * constant for i in range(0, len(auto_corr_y))],
                           'Series' : [series_no] * len(auto_corr_y),
                           'Axis' : [ax_y] * len(auto_corr_y)})
    
    acf_df = pd.concat([acf_df_x, acf_df_y])
    
    if plot_acf == True:
        plot_acf_graph(acf_df_x, acf_df_y, ax_x, ax_y)
    else:
        pass
    return acf_df

def new_scandir(dirname):
    """
    Scanning throught all subfolders and return list of all folders and subfolders
    """
    subfolders= [f.path for f in os.scandir(dirname) if f.is_dir()]
    for dirname in list(subfolders):
        subfolders.extend(new_scandir(dirname))
    return subfolders

def clean_path(folder_path):
    """
    Transform the path from Windows to Linux
    """
    is_prev_slash = False
    for char in folder_path:
        if char in '\\' and not is_prev_slash:
            folder_path = folder_path.replace(char,'/')
            is_prev_slash = True
        elif char in '\\' and is_prev_slash:
            folder_path = folder_path.replace(char, '')
    folder_path = folder_path[1:]
    return folder_path

def find_files(directory,filetype):
    """
    Creates a list of dataset files
    """
    files = []
    folders = []
    itemsindir = new_scandir(directory)
    for item in itemsindir:
        if item.startswith(directory):
            clear_item = item.replace(directory,'')
            clear_item = clean_path(clear_item)+'/'
        folders.append(clear_item)
    for folder in folders:
        for filename in os.listdir(directory+'/'+folder):
            if filename.endswith(filetype):
                files.append(directory+'/'+folder+filename)
    return files

def autocorr_function(datasets, width_line):
    for a in datasets:
        df=pd.read_csv(a)
        df.head()
        print(a)
        acf_df = get_acf(df = df, nlags = 256, series_no = 128, constant = width_line, plot_acf = True)
        acf_df.to_csv((str(a)[:-3]+'_auto.csv'))
        plt.savefig(str(a)[:-3]+'autocorr_function.png', format='png', dpi=1200, bbox_inches='tight')
        #acf_df.to_csv(str(a)[:-3]+' autocorr function.csv', encoding = 'utf-8', index=False)
        
        print(df)
 
def persistance_db(datasets):
    for a in datasets:
        df=pd.read_csv(a)
        df.head()
     
        rips = Rips(maxdim=3)
        diagrams = rips.fit_transform(df)
        X = df.to_numpy()
        X
        gudhi.persistence_graphical_tools._gudhi_matplotlib_use_tex=False
        # Using default parameters. Change it as required 
        rips_complex = gudhi.RipsComplex(distance_matrix=X, max_edge_length=100.0) 		#max_edge_length=100, 250
        simplex_tree = rips_complex.create_simplex_tree(max_dimension=3)
        diag = simplex_tree.persistence(min_persistence=0)
        ans = extract_list_from_raw_data(diag)
        diag_df = pd.DataFrame(ans, columns=["Start", "End", "Length", "Homology group"])
        diag_df.to_csv((str(a)[:-4]+"diag_df_output.csv"))
        #np.savetxt((str(a)[:-3]+'output_data.csv'), diag, delimiter=',', fmt='% s')
        gudhi.plot_persistence_barcode(diag,fontsize=18, legend=True, inf_delta=0.5)
    	#inf_delta=0.1
        plt.xlabel('Sampling length, μm', fontsize = 16)
        plt.ylabel('Topological invariants', fontsize = 18)
        plt.xticks(fontsize = 16)
        plt.yticks(fontsize = 0)
        plt.savefig(str(a)[:-3]+'barcode.png', format='png', dpi=1200, bbox_inches='tight')
    
        gudhi.plot_persistence_diagram(diag,fontsize=18,alpha=0.5,legend=True,inf_delta=0.2, greyblock=False)
    
        plt.xlabel('Feature appearance, μm', fontsize = 18)
        plt.ylabel('Feature disappearance, μm', fontsize = 18)
        plt.xticks(fontsize = 16)
        plt.yticks(fontsize = 16)
        plt.savefig(str(a)[:-3]+'persistence_diagram.png', format='png', dpi=1200, bbox_inches='tight')

def return_min_max_ix(m):
    min_ix = np.unravel_index(m.argmin(), m.shape)
    max_ix = np.unravel_index(m.argmax(), m.shape)
    return [min_ix[0], min_ix[1], max_ix[0], max_ix[1]]
        
def minmax_db(datasets):
    for a in datasets:
        data = pd.read_csv(a, index_col = 'DataLine')
        n = 3
        rows_to_drop = data.shape[0] - int(data.shape[0] / n) * n
        if rows_to_drop < 0:
            raise ValueError('Number of rows to drop cannot be negative.')
        else:
            pass
        if rows_to_drop == 0:
            mat = data.to_numpy()
        else:
            mat = data.iloc[:-rows_to_drop, :-rows_to_drop].to_numpy()
        if mat.shape[0] == mat.shape[1]:
            pass
        else:
            raise ValueError('Please check the dimension of main sqaure matrix.')
        if mat.shape[0] % n == 0:
            pass
        else:
            raise ValueError('Please check the dimension of smaller sqaure matrix.')
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

        sub_mat_df = pd.DataFrame([x.flatten() for x in mat_list],
                                  columns = [f'ri_{i}_ci_{j}' for i in range(n) for j in range(n)])

        min_max_ix_dict = {k + 1 : return_min_max_ix(m) for k, m in enumerate(mat_list)}

        points = pd.DataFrame.from_dict(min_max_ix_dict).T.rename(columns = { 0 : 'min_r', 1 : 'min_c', 2 : 'max_r', 3 : 'max_c'})

        points.head()

        min_df = points.groupby(['min_r', 'min_c']).size().reset_index()
        min_df = min_df.rename(columns = {0 : 'X3', 'min_r' : 'r', 'min_c' : 'c'})
        min_df['type'] = 'min'

        max_df = points.groupby(['max_r', 'max_c']).size().reset_index()
        max_df = max_df.rename(columns = {0 : 'X3', 'max_r' : 'r', 'max_c' : 'c'})
        max_df['type'] = 'max'

        points = pd.concat([min_df, max_df])

        points.to_csv(f'{a[:-4]}_min_max_ix({n}x{n}).csv', index = False)
        sub_mat_df.to_csv(f'{a[:-4]}_flattened_submat({n}x{n}).csv', index = False)
        

