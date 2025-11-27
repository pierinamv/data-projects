import numpy as np
import random

def euclidean(vector1,vector2):
    return np.sqrt(np.sum((vector1-vector2)**2))
def MyKmeans(matriz,n_cluster,n_init=15,max_iter=300,tol=0.0001):
    k = n_cluster
    points = matriz.shape[0]
    dims = matriz.shape[1]

    #max_iter=300
    #t = 0.0001
    tol = np.full(k,tol)

    n_init = 15
    SelInertia = np.full(n_init,np.nan)
    SelLabels = np.full((n_init,points),np.nan)

    for j in range(n_init):

        delta = np.full(k,1)
        Ik_t0 = np.full(k,10000)

        #Inicializo centroides de forma aleatoria
        indexCent = np.random.randint(0,points,size=k) # k indices de los centroides
        Centroids = np.array([matriz[c] for c in indexCent])

        it = 0
        while np.any(delta > tol) and it<max_iter:
    
            LABELS = np.full(points,10)
            for i in range(matriz.shape[0]):
                file=matriz[i]
                dist = [euclidean(file,cent) for cent in Centroids]
    
                label = np.where(dist == np.min(dist))[0][0] #se selecciona el indice del cluster con la distancia mas corta de cada fila a un centroide
                LABELS[i] = label
            #print(LABELS)

            #Redefinir centroides
            inCentroids = np.copy(Centroids)
            Ik = np.arange(k)
            for ki in range(k):
                clusterK = np.array([matriz[bbb] for bbb in np.where(LABELS == ki)[0]])
                Ik[ki]=np.sum(np.sum((clusterK - inCentroids[ki])**2,axis=1),axis=0)
    
                ck = np.mean(clusterK,axis=0)
                if type(ck)==numpy.ndarray:
                    Centroids[ki] = ck
        
            delta = np.abs(Ik_t0 - Ik)
            Ik_t0 = Ik
    
            it=it+1
    
        SelInertia[j]=np.sum(Ik)
        SelLabels[j]=LABELS

    return SelLabels[np.where(SelInertia==np.min(SelInertia))[0][0]]

#Ejemplo:
#labels = MyKmeans(matriz,9,n_init=10) #sugerido n_ini>15