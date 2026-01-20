from pathlib import Path
import pandas as pd
import matplotlib.pyplot as plt

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
cols=df2.filter(regex='^(a0|b0)l[1]$').columns
cols =['i', 'time', *cols]
time=[499]
df2=df2[df2['time'].isin(time)][cols]

plt.plot(df2['i'],df2.iloc[:,2],label=df2.columns[2])
plt.plot(df2['i'],df2.iloc[:,3],label=df2.columns[3])
plt.legend(loc='lower right')
plt.show()