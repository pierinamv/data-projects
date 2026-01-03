import numpy as np

def kmeans(matrix,n_cluster,n_init=25,max_iter=300,tol=1e-12):
    k = n_cluster
    obs = matrix.shape[0]
    vars = matrix.shape[1]

    #tol = np.full(k,tol)
    SelInertia = np.full(n_init,np.nan)
    SelLabels = np.full((n_init,obs),np.nan)
    SelCentroids = np.full((n_init,k,vars),np.nan)

    for j in range(n_init):

        delta = np.full(k,1)
        #Inicializo centroides de forma aleatoria
        Centroids = matrix[np.random.choice(obs,k,replace=False)]# k indices de los centroides
                
        it = 0
        while np.any(delta > tol) and it<max_iter:

            prev_Centroids = Centroids.copy()      
            dist2 =np.sum((matrix[:,None,:]-Centroids[None,:,:])**2,axis=2) #shape(obs,k,vars)
            LABELS = np.argmin(dist2,axis=1)        
            #Redefinir centroides
            for ki in range(k):
                mask = LABELS == ki
                if np.any(mask):
                    Centroids[ki]=matrix[mask].mean(axis=0)
                else:
                    Centroids[ki]=matrix[np.random.choice(obs)]          
                    
            delta=np.linalg.norm(Centroids - prev_Centroids, axis=1)
    
            it=it+1
        dist2 =np.sum((matrix[:,None,:]-Centroids[None,:,:])**2,axis=2) #shape(obs,k,vars)
        LABELS = np.argmin(dist2,axis=1)
        Ik = np.array([np.sum(dist2[LABELS == ki, ki]) for ki in range(k)])

        SelInertia[j]=np.sum(Ik)
        SelLabels[j]=LABELS
        SelCentroids[j]=Centroids

    inBest = np.argmin(SelInertia)
            
    return SelLabels[inBest],SelInertia[inBest],SelCentroids[inBest]        

#Ejemplo:
#labels,inertia,centroids = kmeans(matriz,9,n_init=10) #sugerido n_ini>15