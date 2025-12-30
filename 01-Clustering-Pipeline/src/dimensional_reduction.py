import numpy as np


def pca(matrix, n_components):
    U, sigma, Vt = np.linalg.svd(matrix, full_matrices=False)

    PCs = U[:, :n_components] * sigma[:n_components]
    EOFs = Vt[:n_components, :]

    total_variance = np.sum(sigma**2)
    explained_variance_ratio = (sigma[:n_components]**2) / total_variance

    return PCs, EOFs, explained_variance_ratio
