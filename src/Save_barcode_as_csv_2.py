#!/usr/bin/env python
# coding: utf-8

# In[1]:
#pip install Ripser
#pip install gudhi
# In[6]:
import numpy as np
import pandas as pd
from ripser import Rips
import matplotlib.pyplot as plt
import seaborn as sns
from persim import plot_diagrams
import gudhi


# In[7]:


def extract_list_from_raw_data(diagrams):
  ans = []
  for diagram in diagrams:
    ans.append([diagram[1][0], diagram[1][1], abs(diagram[1][0] - diagram[1][1]), diagram[0]])

  return ans


if __name__ == "__main__":
  data = pd.read_csv('NaOH 70%.csv')


  # In[8]:


  X = data.to_numpy()
  gudhi.persistence_graphical_tools._gudhi_matplotlib_use_tex=False
  rips_complex = gudhi.RipsComplex(distance_matrix=X, max_edge_length=35)
  simplex_tree = rips_complex.create_simplex_tree(max_dimension=3)

  diag = simplex_tree.persistence(min_persistence=0)

  gudhi.plot_persistence_barcode(diag,fontsize=18, legend=False,max_barcodes=90, inf_delta=0.1)
  plt.xlabel('Sampling length, μm', fontsize = 16)
  plt.ylabel('Topological invariants', fontsize = 18)
  plt.xticks(range(0, 50, 10), fontsize = 16, )
  #plt.xticks(fontsize = 16)
  plt.yticks(fontsize = 16)

  plt.show()

  gudhi.plot_persistence_diagram(diag,fontsize=18,alpha=0.5,legend=True,inf_delta=0.2, greyblock=False)
  plt.xlabel('Feature appearance, μm', fontsize = 18)
  plt.ylabel('Feature disappearance, μm', fontsize = 18)
  plt.xticks(fontsize = 16)
  plt.yticks(fontsize = 16)

  # In[12]:


  plt.show()


  # In[15]:


  ans = extract_list_from_raw_data(diag)
  df = pd.DataFrame(ans, columns = ["Start", "End", "Length", "Homology group"])
  df.head()


  # In[16]:


  df.to_csv("Barcode extraction.csv")

