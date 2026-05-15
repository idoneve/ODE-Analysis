"""
Complete example showing how to use dynamic variable configuration
for both first-order and higher-order ODE systems.

Key insight: Just change N_VARS at the top, and everything adapts automatically.
"""

import numpy as np
from ic_generator import generate_ic_grid, get_ic_grid_info
from state_helpers import StateAccessor
from ode_viewer_nD import ODESystemND, ODEViewerND

# ============================================================================
# CONFIGURATION - Change these values at the top only!
# ============================================================================

N_VARS = 3  # Change this to 4, 5, etc. - that's it!

# Initial condition grid settings
IC_CENTER = 0.0  # Or list: [0.0, 0.5, -0.5]
IC_SPREAD = 2.0  # Or list: [1.0, 2.0, 0.5]
ICS_PER_VAR = 2  # Or list: [2, 3, 2]

# Time integration settings
T_START = -5.0
T_END = 50.0
NUM_POINTS = 1000

# System type
IS_FIRST_ORDER = False  # Set to False for higher-order systems
ODE_ORDER = 3  # Only used if IS_FIRST_ORDER = False

# ============================================================================
# SYSTEM DEFINITION
# ============================================================================

if IS_FIRST_ORDER:
    # First-order system: define dx/dt for each variable
    
    if N_VARS == 3:
        VAR_NAMES = ["x", "y", "z"]
        
        def system_func(t, state):
            s = StateAccessor(state, VAR_NAMES)
            dx = np.sin(s.y)
            dy = np.sin(s.z)
            dz = np.sin(s.x)
            return [dx, dy, dz]
    
    elif N_VARS == 4:
        VAR_NAMES = ["x", "y", "z", "w"]
        
        def system_func(t, state):
            s = StateAccessor(state, VAR_NAMES)
            dx = np.sin(s.y)
            dy = np.sin(s.z)
            dz = np.sin(s.w)
            dw = np.sin(s.x)
            return [dx, dy, dz, dw]
    
    else:
        # Generic N-variable cyclic system
        VAR_NAMES = [f"x_{i}" for i in range(N_VARS)]
        
        def system_func(t, state):
            # Each variable's derivative is sine of the next variable
            derivs = []
            for i in range(N_VARS):
                next_idx = (i + 1) % N_VARS
                derivs.append(np.sin(state[next_idx]))
            return derivs

else:
    # Higher-order system: define dⁿx/dtⁿ
    # state = [x, dx/dt, d²x/dt², ..., dⁿx/dtⁿ]
    N_VARS = ODE_ORDER
    VAR_NAMES = ["x"] + [f"x^{i}" for i in range(1, ODE_ORDER)]
    
    def highest_derivative(t, state):
        # Higher-order example: d³x/dt³ = x * d²x/dt² + t²
        if ODE_ORDER == 2:
            # Second order: d²x/dt² = -x - t
            x = state[0]
            return -x - t
        elif ODE_ORDER == 3:
            # Third order: d³x/dt³ = x * d²x/dt² + t²
            x, dx, ddx = state
            return x * ddx + t ** 2
        elif ODE_ORDER == 4:
            # Fourth order: d⁴x/dt⁴ = -x - d²x/dt²
            x, dx, ddx, d3x = state
            return -x - ddx
        else:
            # Generic: dⁿx/dtⁿ = state[0] + state[-1]
            return state[0] + state[-1]

# ============================================================================
# SOLVE THE SYSTEM
# ============================================================================

# Generate IC grid automatically
ic_grid = generate_ic_grid(N_VARS, IC_CENTER, IC_SPREAD, ICS_PER_VAR)
total_ics = get_ic_grid_info(N_VARS, ICS_PER_VAR)

print(f"System: {N_VARS}-variable {'first-order' if IS_FIRST_ORDER else f'{ODE_ORDER}-order'}")
print(f"Variables: {VAR_NAMES}")
print(f"Initial conditions: {total_ics} trajectories")
print(f"Time span: [{T_START}, {T_END}]")
print()

# Create system object
if IS_FIRST_ORDER:
    system = ODESystemND(system_func, N_VARS, VAR_NAMES)
else:
    system = ODESystemND.from_higher_order(highest_derivative, ODE_ORDER, VAR_NAMES)

# Solve all trajectories
t_eval = np.linspace(T_START, T_END, NUM_POINTS)
viewer = ODEViewerND()

viewer.solve_ics_grid(
    system,
    (T_START, T_END),
    ic_grid,
    total_ics,
    t_eval=t_eval,
)

print(f"✓ Solved {len(viewer.solutions)} trajectories")

# ============================================================================
# PLOT RESULTS
# ============================================================================

# For 3+ variable systems, plot first 3 dimensions
projection_axes = [0, 1, 2]  # time, first var, second var

viewer.plot_all_3d(
    projection_axes=projection_axes,
    color_variable=None,
    figsize=(10, 8),
    title=f"{N_VARS}-Variable System",
)

print(f"✓ Plotted phase space")
