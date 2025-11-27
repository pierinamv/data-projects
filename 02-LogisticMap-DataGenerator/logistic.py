import numpy as np
import matplotlib.pyplot as plt

def logistic_map(x,r):
    '''
    Compute one iteration of the logistic map.

    The logistic map is a discrete dynamical system defined by:
    x(t+1) = r * x(t) * (1 - x(t)) 
    
    Here:

         x: Current population ratio (0<x<1). Type: float.
         r: Control parameter. Type: float
     
    Returns:
        The value of the next step, x(t+1). Type: float.
    '''
    return r*x*(1-x)

def generate_data(r,filename,x0=0.1,steps=1200,last=200):
    ''' 
    Write and read the last 200 values.
    '''
    with open(filename,'a') as file:   
        for i in range(steps):
            x=logistic_map(x0,r)
            if(i>=(steps-last)):
                file.write(f"{r}, {x}\n")
            x0=x

def bifurcation_diagram(filename):
    data=np.loadtxt(filename, delimiter=',')
    plt.scatter(data[:,0],data[:,1],s=1)
    plt.xlabel('r');plt.ylabel('x')
    plt.title('Bifurcation diagram of logistic map')
    plt.show()