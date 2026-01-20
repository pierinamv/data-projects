import my_logistic as log
import numpy as np

filename='bifurcation_data.txt'
open(filename,'w').close()

for r in np.linspace(0,4,1000):
    log.generate_data(r,filename)

log.bifurcation_diagram(filename)