import numpy as np; import xarray as xr
def clean_data(data,level):
    data=data.sel(level=level,latitude=np.arange(10,-30.5, -0.5),longitude=np.arange(-90,-29.5,0.5),time=slice('1979-01-01','2022-12-31'), expver = 1)
    data=data.sortby('latitude',ascending=True)
    data=data.sel(time=~((data.time.dt.month == 2) & (data.time.dt.day == 29)))
    data=data.drop_vars(['level','expver'])
    print(data)
    return data

def normalize(data):
    return (data-data.mean(dim='time'))/data.std(dim='time')

def construct_matrix(datax,datay):
    data = xr.merge([datax,datay])
    data = data.stack(space =['latitude','longitude'])
    data=data.to_array(dim="component").transpose('time','component','space')
    data=data.values.reshape(len(data.time),-1) 
    return data

