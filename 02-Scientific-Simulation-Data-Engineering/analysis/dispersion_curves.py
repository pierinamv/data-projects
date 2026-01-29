import numpy as np;
import pandas as pd; 
import matplotlib.pyplot as plt
from pathlib import Path
#from src import plot_dispersion_curves as pdv
base_dir=Path(__file__).resolve().parent.parent
dataexp_dir = Path(base_dir/'data_experiments')

#Figura2 Llamoca et al.
def dispcurve_1layer():
    data1layer = Path(dataexp_dir/'k_sig_gen.dat')
    cols = ['k','sigma','delta','da','db','t_trans','itmax','nmax','dt','dx']
    df = pd.read_csv(data1layer,
            sep=r'\s+',
            header=None,
            comment='#',
            names=cols
            )
    df['delta'] = df['delta'].round(1)
    df = df[df['delta'].isin([1.,2.,3.,5.,7.])]
    dfb = df.loc[:,['k','sigma','delta']].copy()
    plt.scatter(dfb['k'],dfb['sigma'],s=5,color='black',linestyle='-')

def plot_dc(df,fixed_label='v',fvalue=20,groupby_label='delta',u=25,dc1layer=False):
    colors = plt.cm.tab20.colors
    df1=df[df['u']==u]
    df1=df1[df1[fixed_label]==fvalue]
    df1 = df1.loc[:,['k','sigma','delta','v']]
    if fixed_label=='delta':
        df1 = df1[df1['v'].isin([80.,90.,100.,110.,120.,130.,140.,150.,200.,250.])]
    elif fixed_label=='v':
        df1=df1[df1['delta'].isin([0.05,0.1,0.15,0.2,0.25,0.3,0.35,0.5,1.,3.,5.,7.])]
    if dc1layer == True:
        dispcurve_1layer()
    for i,(groupby,group) in enumerate(df1.groupby(groupby_label)):
        plt.plot(group['k'],group['sigma'],
                 linestyle='-',color=colors[i],
                 alpha=0.7,linewidth=1.,
                 label=f'{groupby:.2f}')
    
    plt.xlabel('k');plt.ylabel('sigma')
    plt.grid()
    plt.legend(title=rf'${groupby_label}$', loc='lower right')
    plt.xlim(0,0.1);plt.ylim(-0.02,0.055)
    plt.title(f'Dispersion curve for {fixed_label}={fvalue:.2f}')
    plt.show()

data_dir=Path(dataexp_dir/'concentr_sist12acop.dat')
cols = ['k','sigma','delta','v','da',
        'db','vsr','u','t_trans','itmax',
        'nmax','dt','dx']
df = pd.read_csv(data_dir,
            sep=r'\s+',
            header=None,
            comment='#',
            names=cols
            )

plot_dc(df,fixed_label='delta',fvalue=0.2,groupby_label='v',dc1layer=True)     
plot_dc(df,fixed_label='v',fvalue=250,groupby_label='delta',dc1layer=True)
