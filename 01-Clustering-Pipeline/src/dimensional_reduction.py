import numpy as np

def pca_svd(matrix, n_components,normalized=True):
    '''
    Principal Component Analysis using SVD.

    Parameters
    matrix: ndarray, shape(n_obs,n_features)
    n_components: int
    normalized: bool

    Returns
    PCs: ndarray, shape(n_obs,n_components)
    EOFs: ndarray, shape(n_components,n_features)
    explained_variance: ndarray
    '''
    if normalized ==False:
        matrix=(matrix-np.mean(matrix,axis=0))/np.std(matrix,axis=0)

    U, sigma, Vt = np.linalg.svd(matrix, full_matrices=False)
    PCs = U[:, :n_components] * sigma[:n_components]
    EOFs = Vt[:n_components, :] #cada EOF es una fila de Vt

    total_variance = np.sum(sigma**2)
    explained_variance_ratio = (sigma[:n_components]**2) / total_variance

    return PCs, EOFs, explained_variance_ratio
