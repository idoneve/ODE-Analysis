# ODE Analysis Toolkit

A powerful toolkit for analyzing N-dimensional ODE systems with **dynamic variable configuration**. Change one number and everything adapts automatically—no more manual loop adjustments or broken variable unpacking.

## 🚀 Quick Start (5 Minutes)

```python
N_VARS = 3  # Just change this for number of variables
```

### Step 1: Ensure imports work

```python
import sage.all as sage
import numpy as np
from ic_generator import generate_ic_grid, get_ic_grid_info
from state_helpers import StateAccessor
from ode_viewer_nD import ODESystemND, ODEViewerND
```

### Step 2: Set up configuration

```python
IC_CENTER = 0.0 # Where the center of IC grid is
IC_SPREAD = 2.0 # How far the IC grid spreads too
ICS_PER_VAR = 2 # How many ICs to put on each axis
```

### Step 3: Generate ICs (automatic)

```python
ic_grid = generate_ic_grid(N_VARS, IC_CENTER, IC_SPREAD, ICS_PER_VAR)
total_ics = get_ic_grid_info(N_VARS, ICS_PER_VAR)
```

---

## 📚 Core Modules

| Module | Purpose | Usage |
|--------|---------|-------|
| **ic_generator.py** | Generates N-dimensional IC grids automatically | `generate_ic_grid(n_vars, ic_center, ic_spread, ics_per_var)` |
| **state_helpers.py** | Makes accessing state variables easier (optional) | `StateAccessor(state, var_names)` |
| **ode_viewer_nD.py** | Solve and visualize ODE systems in any dimension | `ODEViewerND().plot_all_3d()` |

---

## 💡 Examples

```python
import sage.all as sage
import numpy as np
from ic_generator import generate_ic_grid, get_ic_grid_info
from state_helpers import StateAccessor
from ode_viewer_nD import ODESystemND, ODEViewerND

# === CONFIGURATION ===
N_VARS = 3 
IC_CENTER = 0.0
IC_SPREAD = 2.0
ICS_PER_VAR = 2

# For a more general initial condition grid
ic_grid = generate_ic_grid(
    n_vars=3,
    ic_center=[0.0, 0.5, -0.5],     # Per-variable centers
    ic_spread=[1.0, 2.0, 0.5],      # Per-variable spreads
    ics_per_var=[2, 3, 2]           # Different counts per dimension
)

# === SYSTEM (circular sin) ===
VAR_NAMES = [f"x_{i}" for i in range(N_VARS)]

def system_func(t, state):
    # Works for any N_VARS
    derivs = []
    for i in range(N_VARS):
        next_idx = (i + 1) % N_VARS
        derivs.append(np.sin(state[next_idx]))
    return derivs

# === SOLVE ===
ic_grid = generate_ic_grid(N_VARS, IC_CENTER, IC_SPREAD, ICS_PER_VAR)
total_ics = get_ic_grid_info(N_VARS, ICS_PER_VAR)

system = ODESystemND(system_func, N_VARS, VAR_NAMES)
t_eval = np.linspace(-5, 50, 1000)

viewer = ODEViewerND()
viewer.solve_ics_grid(system, (-5, 50), ic_grid, total_ics, t_eval=t_eval)
viewer.plot_all_3d(projection_axes=[0, 1, 2])
```

---

## 🎯 Common Patterns

### Pattern 1: Generic System (Any Dimensions)
```python
def system_func(t, state):
    derivs = []
    for i in range(N_VARS):
        next_idx = (i + 1) % N_VARS
        derivs.append(np.sin(state[next_idx]))
    return derivs
```

### Pattern 2: Named State Access
```python
def system_func(t, state):
    s = StateAccessor(state, VAR_NAMES)
    dx = s.x * s.y
    dy = s.y * s.z
    dz = s.z * s.x
    return [dx, dy, dz]
```

### Pattern 3: Higher-Order ODE (e.g., 4th order)
```python
N_VARS = 4  # 4th order
ODE_ORDER = 4
VAR_NAMES = ["x"] + [f"x^{(i)}" for i in range(1, ODE_ORDER)]

def highest_derivative(t, state):
    x, x1, x2, x3 = state
    return x * x2 + t ** 2

ic_grid = generate_ic_grid(N_VARS, 0, 1, 2)
system = ODESystemND.from_higher_order(highest_derivative, ODE_ORDER, VAR_NAMES)
```

## 📖 How to Use

1. Open cooresponding notebook for that system
2. Set up configurations for ICs and display
3. Define the system (Can `StateAccessor` for readable state access)

---

## ✨ Key Features

- ✅ **Change parameters easily** → everything updates
- ✅ **Flexible configuration** -> scalar or per-variable parameters
- ✅ **StateAccessor** -> for easy access to state variables
- ✅ **Scales to any dimensions** -> (2D, 3D, 5D, 10D, ...)

---

## 🐛 Troubleshooting

### I changed N_VARS but got errors
- ✓ Check `VAR_NAMES` has `N_VARS` elements
- ✓ Test your `system_func` with different `N_VARS` values
- ✓ Ensure system equations don't have hardcoded indices

### I want different spreads per variable
```python
ic_grid = generate_ic_grid(
    n_vars=N_VARS,
    ic_center=[0.0, 0.5, -0.5],     # List: per-variable
    ic_spread=[1.0, 2.0, 0.5],      # List: per-variable
    ics_per_var=[2, 3, 2]           # List: per-variable
)
```

---

## 📁 What's Included

- `ic_generator.py` - Auto initial condition grid generation
- `state_helpers.py` - System function helpers for dynamic variable handling (Useful when you want unpacking-like behavior for arbitrary numbers of variables)
- `ode_viewer_nD.py` - ODE solving and visualization library
- Jupyter notebooks: `ODE_Viewer.ipynb`, `ODE_2System_Viewer.ipynb`, `ODE_NSystem_Viewer.ipynb` - For analysis and viewing

---

## 🎓 Example Notebooks

The toolkit includes Jupyter notebooks demonstrating various use cases:

- **ODE_Viewer.ipynb** - Basic ODE visualization
- **ODE_2System_Viewer.ipynb** - Two-variable systems (with poincare section)
- **ODE_NSystem_Viewer.ipynb** - General n-dimensional systems

## TODOs
* refactor notebooks into one single w/ functions in their own library
* add better customizability
    * show/hide init condition points and poincare intersections
    * animation autoscaling
* Fix first and last frames of animation from being outputted
* Make plane sides configurable
* Fix plane so it looks normal past boundary

* Add option for center to be actual center or only positive (use all axis or just positive nums)
* Create graph of fixed points (color coded based on stability) on poincare plots
* Use better fixed point approximations
* Make possible poincare sections not just planes
    * Cylinder
    * Sphere (Mercador Projection?)
    * Multiple planes
    * Torus
* 3D Poincare plot
