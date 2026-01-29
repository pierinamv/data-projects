from pathlib import Path
import pandas as pd
import matplotlib.pyplot as plt

base_dir=Path(__file__).resolve().parent.parent
dataexp_dir = Path(base_dir/'data_experiments')

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

df=df[['k','sigma','delta','v']]
df['delta'] = df['delta'].round(2)
df1=df.groupby(['delta','v']).max().reset_index()
df1.rename(columns={'k':'last_tested_k','sigma':'max_sigma'},inplace=True)
df1=df1[['delta','v','max_sigma','last_tested_k']]
df1.to_csv(dataexp_dir/'max_sigma.csv',index=False)

dictVc={'delta':[],'v_c':[]}
for delta, group in df1.groupby('delta'):
    g1=group[(group['max_sigma']>0.) & (group['max_sigma']<1e-6)]
    try:
        id_vmax=g1['v'].idxmax()
        g1_maxv=g1.loc[id_vmax,:]
        dictVc['delta'].append(g1_maxv['delta'])
        dictVc['v_c'].append(g1_maxv['v'])
    except:
        print(f'Critical velocity for delta={delta:.2f} has not be found')

dfVc=pd.DataFrame(dictVc)
plt.plot(dictVc['delta'],dictVc['v_c'],lw=0.5,ls='--',color='black')
plt.xlim(0.05,0.4);plt.ylim(75,200)
plt.ylabel(r'$v_c$');plt.xlabel(r'$\delta$')
plt.title(r'Critical velocity for linear stability ($\sigma_{\max}<10^{-6}$)')
plt.show()