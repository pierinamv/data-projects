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