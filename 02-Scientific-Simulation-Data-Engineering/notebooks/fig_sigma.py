import pandas as pd
from pathlib import Path
base=Path.cwd()
filesigma=base/'..'/'data_temporal'/'sigma.dat'
df_sigma=pd.read_csv(
    filesigma,
    header=None,
    sep='\s+',
    names=['time','sigma','log_cmax'])

import matplotlib.pyplot as plt

def scatter_plot(data_x,data_y,xlabel,ylabel):
    '''
    Parameters:
    x: variable x, str
    y: variable y, str

    '''
    plt.figure(figsize=(6,3))
    plt.scatter(data_x,data_y,s=1)
    plt.xlabel(xlabel.title());plt.ylabel(ylabel.title())
    plt.grid()
    plt.show()

scatter_plot(df_sigma['time'],df_sigma['sigma'],'time','sigma')
scatter_plot(df_sigma['time'],df_sigma['log_cmax'],'time','log_cmax')

