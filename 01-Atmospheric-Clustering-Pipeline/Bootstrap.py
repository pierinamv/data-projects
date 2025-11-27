import numpy as np
import random

array = np.array([]) #arreglo con las etiquetas de cps desde 1979 hasta 2024

def clustrans(idx):
    mat1=np.zeros((idx.shape[0],9)) #(dimension del array de entrada, #kluster)
    mat1[mat1==0]=np.nan #cambia los zeros a datos nan
    for i in range(0,int(np.max(idx))):
        for j in range(0,int(idx.shape[0]-1)):
            if idx[j]==i+1:
                mat1[j,i]=idx[j+1]
                
    #print(mat1)

    per_trans=np.zeros((9,9)) # cambiat a 9
    for icol in range(0,int(np.max(idx))):
        for iclassd in range(0,int(np.max(idx))):
             per_trans[icol,iclassd]=np.sum(mat1[:,icol]==iclassd+1)*100/(np.sum(~np.isnan(mat1[:,icol])))
    return (per_trans)

# Haciendo la prueba de bootstrap
yg = array.copy()
n=1000
probab=np.zeros((n,9,9))
for i in range(n):
    random.shuffle(yg)
    y=clustrans(yg) 
    probab[i,:,:]=y
probab=np.percentile(probab,90,axis=0)

true90 = clustrans(array) > probab
true90