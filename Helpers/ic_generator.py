import numpy as np
from itertools import product


def generate_ic_grid(n_vars, ic_center, ic_spread, ics_per_var):
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

    ranges = []
    for i in range(n_vars):
        min_val = ic_center[i] - ic_spread[i]
        max_val = ic_center[i] + ic_spread[i]
        linspace = np.linspace(min_val, max_val, ics_per_var[i])
        ranges.append(linspace)

    ic_grid = [list(point) for point in product(*ranges)]

    return ic_grid


def get_ic_grid_info(n_vars, ics_per_var):
    if isinstance(ics_per_var, int):
        ics_per_var = [ics_per_var] * n_vars
    return int(np.prod(ics_per_var))
