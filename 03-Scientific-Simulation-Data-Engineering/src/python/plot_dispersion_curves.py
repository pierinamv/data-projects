import matplotlib.pyplot as plt
import pandas as pd

def dispersion_curve(data,cols,v,ls,labelDelta=False,u=25.):
    #global v
    colors = plt.cm.tab10.colors
    df = pd.DataFrame(data=data,columns=cols)
    df1 = df[df['v']==v]
    df1=df1[df1['u']==u]    
    #u=df['u'].iloc[0]
    df1 = df1.iloc[:,:3]
    df1.head()
    i=0
    for delta, group in df1.groupby('delta'):
        plt.plot(group['k'],group['sigma'],linestyle=ls,color=colors[i],alpha=0.7,linewidth=2.,label=f'{delta:.1f}')
        i+=1

