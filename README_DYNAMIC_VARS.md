# Dynamic Variable Configuration - Summary

## Problem Solved

Previously, changing the number of variables in your ODE system required manual adjustments in multiple places:
- IC grid setup loops (nested for-loops that had to be manually adjusted)
- Variable unpacking in system functions
- Variable names lists

Now, you can change **just one number** at the top of your code and everything adjusts automatically.

## Solution Components

### 1. **ic_generator.py** - Automatic IC Grid Generation

Instead of manually writing nested loops, use:

```python
from ic_generator import generate_ic_grid, get_ic_grid_info

# No matter how many variables you have:
ic_grid = generate_ic_grid(
    n_vars=4,              # Change this number
    ic_center=0.0,         # Applies to all variables
    ic_spread=2.0,         # Applies to all variables
    ics_per_var=2          # Or [2, 2, 2, 2] for per-variable control
)

# Get total count for progress reporting
total_ics = get_ic_grid_info(4, 2)  # Returns 16 (2^4)
```

**Key features:**
- Supports scalar or per-variable parameters
- Works with any number of variables
- No nested loops to maintain
- Automatic product calculation (all combinations)

### 2. **state_helpers.py** - Convenient State Access

Instead of manual unpacking that breaks with different variable counts:

```python
# OLD WAY (breaks when you change N_VARS):
def system_func(t, state):
    x, y, z = state  # What if you have 4 variables now?
    return [...]

# NEW WAY (works for any N_VARS):
from state_helpers import StateAccessor

def system_func(t, state):
    s = StateAccessor(state, VAR_NAMES)
    # Access by name, works for any number of variables
    dx = np.sin(s.y)
    dy = np.sin(s.z)
    dz = np.sin(s.x)
    return [dx, dy, dz]
```

**Alternative - raw indexing:** You can also keep using `state[0], state[1], state[2]` etc., which is also variable-count agnostic.

### 3. **example_dynamic_system.py** - Complete Template

A full working example showing:
- How to set N_VARS at the top
- How to define systems for any number of variables
- How to handle both first-order and higher-order systems
- How to generate IC grids and solve

## Quick Start: Converting Your Notebooks

### Step 1: Add imports
```python
from ic_generator import generate_ic_grid, get_ic_grid_info
from state_helpers import StateAccessor
```

### Step 2: Replace your configuration section

**Before:**
```python
ic_center = [0.0, 0.0, 0.0]
ic_spread = 2.0
num_ics_x = 2
num_ics_y = 2
num_ics_z = 2
```

**After:**
```python
N_VARS = 3  # JUST CHANGE THIS!
IC_CENTER = 0.0
IC_SPREAD = 2.0
ICS_PER_VAR = 2
```

### Step 3: Replace IC grid generation

**Before:**
```python
ic_grid = []
for i in np.linspace(ic_center[0] - ic_spread, ic_center[0] + ic_spread, num_ics_x):
    for j in np.linspace(ic_center[1] - ic_spread, ic_center[1] + ic_spread, num_ics_y):
        for k in np.linspace(ic_center[2] - ic_spread, ic_center[2] + ic_spread, num_ics_z):
            ic_grid.append([i, j, k])
```

**After:**
```python
ic_grid = generate_ic_grid(N_VARS, IC_CENTER, IC_SPREAD, ICS_PER_VAR)
total_ics = get_ic_grid_info(N_VARS, ICS_PER_VAR)
```

### Step 4: Optional - Update system function

**Before:**
```python
def system_func(t, state):
    x, y, z = state
    dx = sin(y)
    dy = sin(z)
    dz = sin(x)
    return [dx, dy, dz]
```

**After (more robust):**
```python
def system_func(t, state):
    s = StateAccessor(state, VAR_NAMES)
    dx = sin(s.y)
    dy = sin(s.z)
    dz = sin(s.x)
    return [dx, dy, dz]
```

Or even simpler - just index directly:
```python
def system_func(t, state):
    dx = sin(state[1])
    dy = sin(state[2])
    dz = sin(state[0])
    return [dx, dy, dz]
```

## Use Cases

### Case 1: Quickly test different system sizes
```python
for n in [2, 3, 4, 5]:
    N_VARS = n
    ic_grid = generate_ic_grid(N_VARS, 0.0, 2.0, 2)
    # Run and visualize
```

### Case 2: Higher-order derivatives
```python
N_VARS = 4  # 4th order ODE
ODE_ORDER = 4

def highest_derivative(t, state):
    # state = [x, x', x'', x''']
    # Define d4x/dt4 in terms of state
    return state[0] * state[2] + t ** 2
```

### Case 3: Mixed variable spreads
```python
# Different spreads for each variable
ic_grid = generate_ic_grid(
    n_vars=3,
    ic_center=[0.0, 0.5, -0.5],
    ic_spread=[1.0, 2.0, 0.5],
    ics_per_var=[2, 3, 2]  # Different counts per variable
)
```

## Files Created

1. **ic_generator.py** - Core IC generation utilities
2. **state_helpers.py** - State access helpers (optional but recommended)
3. **example_dynamic_system.py** - Full working example
4. **EXAMPLE_USAGE.md** - Detailed usage guide
5. **README.md** - This file (summary and quick start)

## Testing

All modules have been tested:
```bash
python3 ic_generator.py  # Tests the IC generator with various inputs
python3 state_helpers.py  # Tests state access patterns
```

## Migration Effort

- **Easy**: For systems with straightforward IC generation → 5 min per notebook
- **Medium**: For systems with complex state unpacking → 10 min per notebook
- **Hard**: For systems with highly specific IC patterns → 15 min (but still worth it!)

Most notebooks should take < 10 minutes to update.

## Next Steps

1. Choose a notebook to update
2. Follow the "Converting Your Notebooks" section above
3. Test by changing `N_VARS` and verifying the system still runs
4. Enjoy never manually adjusting loops again!
