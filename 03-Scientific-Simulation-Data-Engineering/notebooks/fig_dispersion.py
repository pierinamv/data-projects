import numpy as np;import pandas as pd; import matplotlib.pyplot as plt
from pathlib import Path
from src import plot_dispersion_curves as pdv
base_dir = Path(__file__).resolve().parent
data_dir = base_dir #/'experiments'
print(base_dir)

data = np.loadtxt(data_dir/'concentr_sist12acop.dat')#'diffy_taylor_limiteV.dat')
cols = ['k','sigma','delta','v','da','db','vsr','u','t_trans','itmax','nmax','dt','dx']
v = float(input()) #0.010,0.64,2.25

#pdv.dispersion_curve(data,cols,v,'-',labelDelta=True,u=0.)
pdv.dispersion_curve(data,cols,v,'--',labelDelta=True,u=25.)
#plt.axhline(0,linestyle='--',linewidth=0.45,color='black')
plt.legend()
plt.xlim(0,0.5);plt.ylim(-0.005,0.005)
#plt.xlabel('k');plt.ylabel('sigma')
#plt.title(fr'Curvas de dispersión con $\frac{{v^{2}}}{{8u}}$={(v**2)/(8*u):.3f}')

#Figura2 Llamoca et al.
database = np.loadtxt(data_dir/'k_sig_gen.dat')
colss = ['k','sigma','delta','da','db','t_trans','itmax','nmax','dt','dx']
df = pd.DataFrame(data=database,columns=colss)
df['delta'] = df['delta'].round(1)
df = df[df['delta'].isin([1.,2.,3.,5.,7.])]
dfb = df.iloc[:,:3].copy()
plt.scatter(dfb['k'],dfb['sigma'],s=5,color='black',linestyle='-')

plt.show()