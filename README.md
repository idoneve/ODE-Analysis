# ODE Driver and Helper Library

This repository provides a config-driven ODE workflow with reusable helper code under `Helpers/` and a single unified notebook entrypoint: `driver.ipynb`.

## What this repo does

- Loads `config.yaml`
- Builds an ODE system from a user-defined system function
- Generates an initial condition grid
- Solves all trajectories with `ODEViewerND`
- Plots 3D phase-space trajectories
- Computes and renders Poincaré section crossings
- Optionally creates an animated Poincaré plane transition

## Requirements

- Python 3.10+
- `numpy`
- `matplotlib`
- `scipy`
- `PyYAML`

Install dependencies with:

```bash
pip install numpy matplotlib scipy pyyaml
```

## How to use `driver.ipynb`

1. Open `driver.ipynb`
2. Define your ODE system in the `system_func` cell
3. Adjust settings in `config.yaml`
4. Run the notebook cells in order

The driver notebook now mirrors the original `ODE_NSystem_Viewer.ipynb` flow:

1. Load configuration
2. Define the ODE system
3. Generate initial conditions
4. Solve trajectories
5. Compute Poincaré crossings
6. Plot phase-space and Poincaré results
7. Animate the Poincaré plane transition

## Configurable settings

The `config.yaml` file includes:

- `system`: variable count, first-order flag, variable names
- `integration`: time span, point count, step size, boundary cutoff
- `ic_grid`: center, spread, and grid density
- `plot_3d`: projection axes, colormap, title, save path, boundary limits
- `threejs`: enable interactive Three.js export, output HTML file, background and point size
- `poincare`: plane coefficients, enable/disable, output paths
- `animation`: animation enable, start/end planes, fps, duration, save path
- `integration.show_progress`: enable solver progress printing during trajectory integration

## Driver usage example

In `driver.ipynb`, set up your system like this:

```python
# Example 3-variable first-order system

def system_func(t, state):
    x, y, z = state
    dx = 0.3 * x - 0.4 * y * z - 0.15 * x
    dy = 0.3 * y + 0.2 * z - 0.3 * y
    dz = 1.0 * x - 0.5 * y - 0.2 * z
    return [dx, dy, dz]
```

Then run the notebook cells. The driver will print progress during integration and save plots to the paths configured in `config.yaml`.

## File layout

- `driver.ipynb` — unified notebook entrypoint
- `config.yaml` — tuning and plotting settings
- `Helpers/config_loader.py` — loads YAML config
- `Helpers/ic_generator.py` — builds adaptive initial condition grids
- `Helpers/ode_viewer_nD.py` — solver and visualization utilities
- `Helpers/ode_driver.py` — orchestration functions for the notebook
- `Helpers/poincare.py` — Poincaré plane utilities and plotting helpers
- `Helpers/state_helpers.py` — dynamic state accessor for labeled variables

## Notes

- The driver uses a config-first orchestration model.
- `driver.ipynb` now follows the same order as `ODE_NSystem_Viewer.ipynb`.
- Poincaré plotting is split into upward and downward crossings.
- Animation is optional and controlled by `config.yaml`.

## Optional improvements

- Add Three.js interactive viewer support
- Add better boundary clipping on trajectories
- Add richer per-trajectory labels and color legends
