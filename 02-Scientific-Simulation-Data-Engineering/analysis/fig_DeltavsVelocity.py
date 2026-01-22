import numpy as np;import pandas as pd; import matplotlib.pyplot as plt
from pathlib import Path

base_dir=Path(__file__).resolve().parent.parent
file=Path(base_dir/'data_experiments'/'vel_vs_maxSigma.dat')

data = np.loadtxt(file)
cols = ['v','max_sigma','delta']
#v = float(input()) #0.010,0.64,2.25
df = pd.DataFrame(data=data,columns=cols)
df1 = df.loc[:,['v','max_sigma','delta']]
df1['delta'] = df1['delta'].round(2)
#df1.head()
dict1={'delta':[],'v_c':[]}
i=0
for delta, group in df1.groupby('delta'):
    g1=group[group['max_sigma']<1e-6]
    g1_maxv=g1.loc[[g1['v'].idxmax()]]
    dict1['delta'].append(g1_maxv['delta'])
    dict1['v_c'].append(g1_maxv['v'])
    plt.scatter(g1_maxv['delta'],g1_maxv['v'],lw=2.,color='black',s=10)
    plt.text(g1_maxv['delta'].iloc[0]-0.005,g1_maxv['v'].iloc[0]+2.5,f"{g1_maxv['v'].iloc[0]:.0f}",fontsize=9)

plt.plot(dict1['delta'],dict1['v_c'],lw=0.5,ls='--',color='black')
plt.xlim(0.05,0.4);plt.ylim(75,200)
plt.ylabel(r'$v_c$');plt.xlabel(r'$\delta$')
plt.title(r'Critical velocity for linear stability ($\sigma_{\max}<10^{-6}$)')
plt.show()