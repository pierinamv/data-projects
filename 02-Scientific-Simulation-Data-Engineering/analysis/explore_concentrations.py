from pathlib import Path
import matplotlib.pyplot as plt
import pandas as pd

base_dir=Path(__file__).resolve().parent.parent
files_dir=Path(base_dir/'data_temporal')
files = files_dir.glob('t*.dat')
print(base_dir)

dfs=[]
cols=['i',
      'a0l1','a0l2','a1l1','a1l2','a2l1','a2l2',
      'b0l1','b0l2','b1l1','b1l2','b2l1','b2l2']
for f in files: 
    df=pd.read_csv(
        f,
        header=None,
        sep='\s+',
        comment='#',
        names=cols)
    t=int(f.stem.split('_')[-1]) #stem:name of the file without extension;name, suffix
    df['time']=t
    dfs.append(df)

df_all = pd.concat(dfs,ignore_index=True)

df2=df_all.copy()

def select_vars(df,time,vars=['a0','b0'],layers=['l1']):
    cols=df.filter(regex=f'^({"|".join(vars)})({"|".join(layers)})$').columns
    #cols=df2.filter(regex=f'^(a0|b0)l[1]$').columns
    cols =['i', 'time', *cols]
    df=df[df['time'].isin(time)][cols]
    return df

df2=select_vars(df2,[149,299,599],['a0','b0'],['l1'])

nvars=df2.columns.shape[0]-2
nt=df2['time'].nunique()

for it, (t,group) in enumerate(df2.groupby('time')):
    colors = plt.cm.tab10.colors
    for n in range(nvars):
        plt.plot(group['i'],
                 group.iloc[:,n+2],
                 label=f'{group.columns[n+2]}  (t={t:.0f})',
                 color=colors[n],
                 alpha=(it+1)/nt)

plt.legend(loc='upper right')
plt.show()