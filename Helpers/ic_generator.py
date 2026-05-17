"""
Helper module for generating initial condition grids dynamically.
Supports any number of variables without manual loop adjustments.
"""
import numpy as np
from itertools import product


def generate_ic_grid(n_vars, ic_center, ic_spread, ics_per_var):
    """
    Generate initial condition grid for n-dimensional systems.
    
    Parameters
    ----------
    n_vars : int
        Number of variables in the system
    ic_center : list or float
        Center point for IC grid (length must equal n_vars)
        If float, uses same center for all variables
    ic_spread : float or list
        Spread around center. If list, must equal n_vars length
    ics_per_var : int or list
        Number of ICs along each dimension
        If int, uses same count for all dimensions
        If list, must equal n_vars length
    
    Returns
    -------
    list of lists
        Grid of initial conditions, each of length n_vars
    """
    # Normalize inputs
    if isinstance(ic_center, (int, float)):
        ic_center = [ic_center] * n_vars
    elif len(ic_center) != n_vars:
        raise ValueError(f"ic_center length {len(ic_center)} != n_vars {n_vars}")
    
    if isinstance(ic_spread, (int, float)):
        ic_spread = [ic_spread] * n_vars
    elif len(ic_spread) != n_vars:
        raise ValueError(f"ic_spread length {len(ic_spread)} != n_vars {n_vars}")
    
    if isinstance(ics_per_var, int):
        ics_per_var = [ics_per_var] * n_vars
    elif len(ics_per_var) != n_vars:
        raise ValueError(f"ics_per_var length {len(ics_per_var)} != n_vars {n_vars}")
    
    # Generate linspaces for each variable
    ranges = []
    for i in range(n_vars):
        min_val = ic_center[i] - ic_spread[i]
        max_val = ic_center[i] + ic_spread[i]
        linspace = np.linspace(min_val, max_val, ics_per_var[i])
        ranges.append(linspace)
    
    # Generate all combinations
    ic_grid = [list(point) for point in product(*ranges)]
    
    return ic_grid


def get_ic_grid_info(n_vars, ics_per_var):
    """
    Get information about the IC grid without generating it.
    Useful for progress reporting.
    
    Parameters
    ----------
    n_vars : int
        Number of variables
    ics_per_var : int or list
        Number of ICs per variable
    
    Returns
    -------
    int
        Total number of initial conditions
    """
    if isinstance(ics_per_var, int):
        ics_per_var = [ics_per_var] * n_vars
    return int(np.prod(ics_per_var))
