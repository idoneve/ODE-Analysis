# Dynamic Variable Count - Updated Usage Guide

## Key Changes

The new `ic_generator` module allows you to change the number of variables without manually adjusting loops or unpacking statements.

## Before (Manual Approach)

```python
# Had to manually adjust everything:
ic_center = [0.0, 0.0, 0.0]  # Change this
ic_spread = 2.0
num_ics_x = 2
num_ics_y = 2
num_ics_z = 2

# Had to manually create nested loops:
ic_grid = []
for i in np.linspace(ic_center[0] - ic_spread, ic_center[0] + ic_spread, num_ics_x):
    for j in np.linspace(ic_center[1] - ic_spread, ic_center[1] + ic_spread, num_ics_y):
        for k in np.linspace(ic_center[2] - ic_spread, ic_center[2] + ic_spread, num_ics_z):
            ic_grid.append([i, j, k])  # Also had to change unpacking here
```

## After (Automatic Approach)

```python
from ic_generator import generate_ic_grid, get_ic_grid_info

# Just set these two things:
n_vars = 3  # Change this to 4, 5, etc.
ics_per_var = 2  # Or [2, 2, 2] for different counts per variable

# And optionally configure the center/spread (defaults to scalars):
ic_center = 0.0  # Works for any n_vars
ic_spread = 2.0  # Works for any n_vars

# That's it! IC generation is automatic:
ic_grid = generate_ic_grid(n_vars, ic_center, ic_spread, ics_per_var)
total_ics = get_ic_grid_info(n_vars, ics_per_var)
```

## Features

### Flexible Input
All parameters accept both scalars and lists:

```python
# Scalar - applies to all variables
generate_ic_grid(n_vars=3, ic_center=0.0, ic_spread=2.0, ics_per_var=2)

# List - per-variable control
generate_ic_grid(
    n_vars=3,
    ic_center=[0.0, 0.5, -0.5],    # Different center per var
    ic_spread=[1.0, 2.0, 0.5],     # Different spread per var
    ics_per_var=[2, 3, 2]          # Different count per var
)
```

### Works with Higher-Order Systems

For higher-order derivatives (e.g., 4th order ODE = 4 variables):

```python
# Before: Manual setup of 4-variable system was cumbersome
# After: Just set n_vars and everything adapts

n_vars = 4  # 4th order ODE
ode_order = 4
var_names = ["x"] + [f"x^{(i)}" for i in range(1, ode_order)]

def highest_derivative(t, state):
    # state has n_vars elements, no manual unpacking needed
    return state[0] * state[2] + t ** 2

ic_grid = generate_ic_grid(n_vars=4, ic_center=0.0, ic_spread=1.0, ics_per_var=2)
```

## Updated Notebook Template

See the notebook cells below for a complete example of using the dynamic approach:

```python
# Cell 1: Imports
import numpy as np
from ic_generator import generate_ic_grid, get_ic_grid_info
from ode_viewer_nD import ODESystemND, ODEViewerND

# Cell 2: Configuration
n_vars = 3  # Change this to 4, 5, etc. - that's it!
ics_per_var = 2

# Common settings (defaults work for any n_vars)
ic_center = 0.0
ic_spread = 2.0
t_start = -5.0
t_end = 50.0
num_points = 1000

# Cell 3: System Definition (same as before)
var_names = ["x", "y", "z"]

def system_func(t, state):
    # Use state[0], state[1], state[2], ... instead of unpacking
    x, y, z = state
    dx = np.sin(y)
    dy = np.sin(z)
    dz = np.sin(x)
    return [dx, dy, dz]

# Cell 4: Generate IC Grid (now automatic!)
ic_grid = generate_ic_grid(n_vars, ic_center, ic_spread, ics_per_var)
total_ics = get_ic_grid_info(n_vars, ics_per_var)

# Cell 5: Solve and Plot (same as before)
system = ODESystemND(system_func, n_vars, var_names)
t_eval = np.linspace(t_start, t_end, num_points)
viewer = ODEViewerND()

viewer.solve_ics_grid(
    system,
    (t_start, t_end),
    ic_grid,
    total_ics,
    t_eval=t_eval,
)

viewer.plot_all_3d(projection_axes=[1, 2, 3])
```

## Migration Guide

To update your existing notebooks:

1. Add import at top:
   ```python
   from ic_generator import generate_ic_grid, get_ic_grid_info
   ```

2. Replace IC grid creation section with:
   ```python
   ic_grid = generate_ic_grid(n_vars, ic_center, ic_spread, ics_per_var)
   total_ics = get_ic_grid_info(n_vars, ics_per_var)
   ```

3. Replace the manual nested loop section entirely with the one-liner above.

4. For system functions, you can still use unpacking (e.g., `x, y, z = state`) for clarity, but it now works for any number of variables as long as you define `var_names` and `n_vars` correctly at the top.
