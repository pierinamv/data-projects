import numpy as np
import matplotlib.pyplot as plt

def logistic_map(x,r):
    '''
    Compute one iteration of the logistic map.

    The logistic map is a discrete dynamical system defined by:
    x(t+1) = r * x(t) * (1 - x(t)) 
    
    Parameters
        x: float
            Current population ratio (0<x<1).
        r: float
            Control parameter. 
     
    Returns: float
            The value of the next step, x(t+1).
    '''
    return r*x*(1-x)

def generate_data(r,filename,x0=0.1,steps=1200,last=200):
    ''' 
    Generates the last 'last' values iterated of the logistic map and append them to a file.

    Parameters         
        r: float
            Control parameter of the logistic map. 
        filename: str
            Output file. Created if does not exist.
        x0: float
            Initial population ratio. Default is 0.1.
        steps: int
            Total number of iterations.
        last: int
            Number of iterations to record in the file.

    '''
    with open(filename,'a') as file:   
        for i in range(steps):
            x=logistic_map(x0,r)
            cut=steps-last
            if(i>=cut):
                file.write(f"{r},{x}\n")
            x0=x

def bifurcation_diagram(filename):
    '''
    Plot the bifurcation diagram with values of the file 'filename'.
    '''
    data=np.loadtxt(filename, delimiter=',')
    plt.scatter(data[:,0],data[:,1],s=1)
    plt.xlabel('r');plt.ylabel('x')
    plt.title('Bifurcation diagram of logistic map')
    plt.show()