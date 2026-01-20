## Eligo numero de PCs y aplico kmeans
from sklearn.cluster import KMeans
import numpy as np
from pathlib import Path
base_dir= Path(__file__).resolve().parent.parent
data_dir=base_dir/'data'/'processed'

pcs=np.load(data_dir/'pcs.npy')
mycps=np.load(data_dir/'cps.npy')

kmeans=KMeans(n_clusters=9,random_state=0,n_init=10).fit(pcs)
cps=kmeans.labels_+1
centers = kmeans.cluster_centers_

import pandas as pd
matriz_coinc = np.zeros((9, 9))
for i in range(1, 10): #fila (850hPa)
    for j in range(1, 10): #columna (200hPa)
        tot = np.sum(cps == i)
        matriz_coinc[i-1, j-1] = (np.sum((cps== i) & (mycps == j))/tot)*100

CP_200 = ['1-REF','2-REF','3-REF','4-REF','5-REF','6-REF','7-REF','8-REF','9-REF']
CP_ = ['CP1','CP2','CP3','CP4','CP5','CP6','CP7','CP8','CP9']

df = pd.DataFrame(matriz_coinc, columns=CP_, index=CP_200)
df = df.round(1)
df=df.reset_index()
print(df)