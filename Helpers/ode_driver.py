import numpy as np

from .config_loader import load_config
from .ic_generator import generate_ic_grid
from .ode_viewer_nD import ODESystemND, ODEViewerND


def load_driver_config(config_path="config.yaml"):
    config = load_config(config_path)
    if not isinstance(config, dict):
        raise ValueError("Loaded config must be a mapping")
    return config


def get_system_settings(config):
    system_config = config.get("system", {})
    n_vars = int(system_config.get("n_vars", 3))
    first_order = bool(system_config.get("first_order", True))
    ode_order = system_config.get("ode_order")
    var_names = system_config.get("var_names", [f"x_{i + 1}" for i in range(n_vars)])
    return {
        "n_vars": n_vars,
        "first_order": first_order,
        "ode_order": ode_order,
        "var_names": var_names,
    }


def get_integration_settings(config):
    integration = config.get("integration", {})
    t_start = float(integration.get("t_start", 0.0))
    t_end = float(integration.get("t_end", 1.0))
    num_points = int(integration.get("num_points", 1000))
    step_size = float(integration.get("step_size", 1e-3))
    compute_boundary = integration.get("compute_boundary")
    if compute_boundary is not None:
        compute_boundary = float(compute_boundary)
    return {
        "t_start": t_start,
        "t_end": t_end,
        "num_points": num_points,
        "step_size": step_size,
        "compute_boundary": compute_boundary,
    }


def get_plot_3d_settings(config):
    plot_3d = config.get("plot_3d", {})
    return {
        "projection_axes": plot_3d.get("projection_axes", [0, 1, 3]),
        "color_by": plot_3d.get("color_by", 2),
        "figsize": tuple(plot_3d.get("figsize", [6, 6])),
        "title": plot_3d.get("title", "Phase Space"),
        "colormap": plot_3d.get("colormap", "viridis"),
        "save_path": plot_3d.get("save_path", "./Plots/3D/3D_NSYS_ODE.png"),
    }


def get_poincare_settings(config):
    poincare = config.get("poincare", {})
    return {
        "enabled": bool(poincare.get("enabled", False)),
        "plane": tuple(poincare.get("plane", [1, 0, 0, -3])),
        "point_size": float(poincare.get("point_size", 0.6)),
        "flip_x": bool(poincare.get("flip_x", False)),
        "flip_y": bool(poincare.get("flip_y", False)),
    }


def get_animation_settings(config):
    animation = config.get("animation", {})
    return {
        "enabled": bool(animation.get("enabled", False)),
        "start_plane": tuple(animation.get("start_plane", [1, 0, 0, -0.01])),
        "end_plane": tuple(animation.get("end_plane", [1, 0, 0, -299.99])),
        "duration": float(animation.get("poincare_animation_duration", 15)),
        "fps": int(animation.get("poincare_animation_fps", 24)),
        "trail_length": int(animation.get("poincare_animation_trail", 3)),
        "save_path": animation.get("poincare_animation_save", "./Plots/2D/poincare_animation.html"),
    }


def build_initial_conditions(config):
    system_settings = get_system_settings(config)
    ic_config = config.get("ic_grid", {})
    return generate_ic_grid(
        system_settings["n_vars"],
        ic_config.get("center", [0.0] * system_settings["n_vars"]),
        ic_config.get("spread", 1.0),
        ic_config.get("ics_per_var", [8] * system_settings["n_vars"]),
    )


def build_system(config, system_func=None, highest_derivative=None):
    system_settings = get_system_settings(config)
    if system_settings["first_order"]:
        if system_func is None:
            raise ValueError("A first-order system function must be provided")
        return ODESystemND(system_func, system_settings["n_vars"], system_settings["var_names"])

    if highest_derivative is None:
        raise ValueError("A highest_derivative function is required for higher-order systems")

    if system_settings["ode_order"] is None:
        raise ValueError("ode_order must be defined for higher-order systems")

    return ODESystemND.from_higher_order(
        highest_derivative,
        int(system_settings["ode_order"]),
        system_settings["var_names"],
    )


def solve_initial_conditions(config, system, initial_conditions):
    integration = get_integration_settings(config)
    t_eval = np.linspace(integration["t_start"], integration["t_end"], integration["num_points"])
    viewer = ODEViewerND()
    viewer.solve_ics_grid(
        system,
        (integration["t_start"], integration["t_end"]),
        initial_conditions,
        len(initial_conditions),
        t_eval=t_eval,
        max_step=integration["step_size"],
    )
    return viewer


def plot_phase_space(viewer, config):
    plot_3d = get_plot_3d_settings(config)
    return viewer.plot_all_3d(
        projection_axes=plot_3d["projection_axes"],
        color_variable=plot_3d["color_by"],
        figsize=plot_3d["figsize"],
        title=plot_3d["title"],
        save_path=plot_3d["save_path"],
        compute_boundary=get_integration_settings(config)["compute_boundary"],
    )


def compute_poincare(viewer, config):
    poincare = get_poincare_settings(config)
    if not poincare["enabled"]:
        return []
    intersection = viewer.compute_poincare_intersections(
        projection_axes=get_plot_3d_settings(config)["projection_axes"],
        plane=poincare["plane"],
        compute_boundary=get_integration_settings(config)["compute_boundary"],
        color_variable=get_plot_3d_settings(config)["color_by"],
    )
    return intersection


def plot_poincare(viewer, config, save_path="./Plots/2D/poincare_section.png"):
    intersections = compute_poincare(viewer, config)
    if not intersections:
        return None
    poincare = get_poincare_settings(config)
    return viewer.plot_poincare_section(
        projection_axes=get_plot_3d_settings(config)["projection_axes"],
        plane=poincare["plane"],
        compute_boundary=get_integration_settings(config)["compute_boundary"],
        color_variable=get_plot_3d_settings(config)["color_by"],
        figsize=get_plot_3d_settings(config)["figsize"],
        title="Poincaré Section",
        save_path=save_path,
        show=True,
    )


def animate_poincare(viewer, config):
    animation = get_animation_settings(config)
    if not animation["enabled"]:
        return None
    return viewer.animate_poincare_section(
        start_plane=animation["start_plane"],
        end_plane=animation["end_plane"],
        projection_axes=get_plot_3d_settings(config)["projection_axes"],
        duration=animation["duration"],
        fps=animation["fps"],
        trail_length=animation["trail_length"],
        compute_boundary=get_integration_settings(config)["compute_boundary"],
        color_variable=get_plot_3d_settings(config)["color_by"],
        figsize=get_plot_3d_settings(config)["figsize"],
        save_path=animation["save_path"],
    )
