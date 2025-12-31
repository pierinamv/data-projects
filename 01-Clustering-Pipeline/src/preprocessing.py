import numpy as np; import xarray as xr

def clean_data(data,level):
    '''
    Cleaning data.

    Parameters
    data: DataArray,dim:level,latitude,longitude,time
    level: int

    Returns
    data: DataArray,dim:latitude,longitude,time
    '''
    data=data.sel(level=level,latitude=np.arange(10,-29.5, -0.5),longitude=np.arange(-90,-29.5,0.5),time=slice('1979-01-01','2022-12-31'), expver = 1)
    data=data.sortby('latitude',ascending=True)
    data=data.sel(time=~((data.time.dt.month == 2) & (data.time.dt.day == 29)))
    data=data.drop_vars(['level','expver'])
    #print(data)
    return data

def config(data,ini_year,fin_year):
    '''
    Configuration of time.

    Parameters
    data: DataArray,dim:level,latitude,longitude,time
    ini_year: int
    fin_year: int

    Returns
    data: DataArray,dim:level,latitude,longitude,time
    '''
    data=data.sel(time=slice(f'{ini_year}-01-01',f'{fin_year}-12-31'))
    return data

def normalize(data):
    return (data-data.mean(dim='time'))/data.std(dim='time')

def construct_matrix(datax,datay):
    '''
    Construc matrix for PCA with two datasets.

    Parameters
    datax: DataArray, dims: time,longitude,latitude
    datay: DataArray, dims: time,longitude,latitude

    Returns
    data : ndarray, shape(n_time,n_long*n_lat*2)    

    '''
    data = xr.merge([datax,datay])
    data = data.stack(space =['latitude','longitude'])
    data=data.to_array(dim="component").transpose('time','component','space')
    data=data.values.reshape(len(data.time),-1) 
    return data

