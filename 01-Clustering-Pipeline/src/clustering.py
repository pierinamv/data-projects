import numpy as np

def kmeans(matriz,n_cluster,n_init=15,max_iter=300,tol=0.0001):
    k = n_cluster
    obs = matriz.shape[0]
    vars = matriz.shape[1]

    #t = 0.0001
    tol = np.full(k,tol)

    SelInertia = np.full(n_init,np.nan)
    SelLabels = np.full((n_init,obs),np.nan)

    for j in range(n_init):

        delta = np.full(k,1)
        Ik_t0 = np.full(k,10000)

        #Inicializo centroides de forma aleatoria
        Centroids = matriz[np.random.choice(obs,k,replace=False)]# k indices de los centroides

        it = 0
        while np.any(delta > tol) and it<max_iter:
              
            dist2 =np.sum((matriz[:,None,:]-Centroids[None,:,:])**2,axis=2) #shape(obs,k,vars)
            LABELS = np.argmin(dist2,axis=1) #shape(obs)
            #print(LABELS)

            #Redefinir centroides
            Ik = np.arange(k)
            for ki in range(k):
                mask = LABELS == ki
                if np.any(mask):
                    Centroids[ki]=matriz[mask].mean(axis=0)
                else:
                    pass
               
            Ik = np.array([np.sum(dist2[LABELS == ki, ki]) for ki in range(k)])
        
            delta = np.abs(Ik_t0 - Ik)
            Ik_t0 = Ik
    
            it=it+1
    
        SelInertia[j]=np.sum(Ik)
        SelLabels[j]=LABELS

    return SelLabels[np.where(SelInertia==np.min(SelInertia))[0][0]]

#Ejemplo:
#labels = MyKmeans(matriz,9,n_init=10) #sugerido n_ini>15