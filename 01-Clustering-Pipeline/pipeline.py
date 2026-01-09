import xarray as xr; import numpy as np
from pathlib import Path
base_dir = Path(__file__).resolve().parent
data_dir = base_dir /'data'/'raw'/'ERA5'

wind_x=xr.open_dataset(data_dir / 'vectorU_1979_2022_ERA5.nc') # viento zonal: oeste a este
wind_y=xr.open_dataset(data_dir / 'vectorV_1979_2022_ERA5.nc')

from src.preprocessing import clean_data,normalize, construct_matrix,config
from src.dimensional_reduction import pca_svd
wind_x = clean_data(wind_x,level=200)
wind_y = clean_data(wind_y,level=200)

y1, y2 = 2000, 2010
wind_x =config(wind_x,y1,y2)
wind_y =config(wind_y,y1,y2)

nwindx = normalize(wind_x)
nwindy = normalize(wind_y)

matrix = construct_matrix(nwindx,nwindy)
n=40
pcs,_,var=pca_svd(matrix,n,normalized=True)

print(f'Varianza total explicada por los {n} primeros componentes principales: {np.sum(var)*100:.2f} %')

from src.clustering import kmeans
mycps,inertia,centroids=kmeans(pcs,9)
mycps=mycps+1
print(mycps)