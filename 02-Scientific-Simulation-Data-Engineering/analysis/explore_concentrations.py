from pathlib import Path
import matplotlib.pyplot as plt
import pandas as pd

files = Path('../data_temporal').glob('t*.dat')

dfs=[]
cols=['i',
      'a0l1','a0l2','a1l1','a1l2','a2l1','a2l2',
      'b0l1','b0l2','b1l1','b1l2','b2l1','b2l2']
for f in files: 
    df=pd.read_csv(
        f,
        header=None,
        sep='\s+',
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

df2=select_vars(df2,[49,99,199,299],['a0'],['l1','l2'])

print(df2)

for t,group in df2.groupby('time'):
    plt.plot(group['i'],group.iloc[:,2],label=f'{group.columns[2]}-(t={t:.0f})')
    plt.plot(group['i'],group.iloc[:,3],label=f'{group.columns[3]}-(t={t:.0f})')
    #plt.plot(df2['i'],df2.iloc[:,4],label=df2.columns[4])
plt.legend(loc='lower right')
plt.show()