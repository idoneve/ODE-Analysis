import json
import os
import numpy as np
import matplotlib.pyplot as plt

from .config_loader import load_config
from .ic_generator import generate_ic_grid
from .ode_viewer_nD import ODESystemND, ODEViewerND
from .poincare import plot_poincare_section


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
    show_progress = bool(integration.get("show_progress", True))
    return {
        "t_start": t_start,
        "t_end": t_end,
        "num_points": num_points,
        "step_size": step_size,
        "compute_boundary": compute_boundary,
        "show_progress": show_progress,
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
        "save_plot": bool(plot_3d.get("save_plot", True)),
        "max_boundary": plot_3d.get("max_boundary"),
    }


def get_threejs_settings(config):
    threejs = config.get("threejs", {})
    return {
        "enabled": bool(threejs.get("enabled", False)),
        "save_path": threejs.get("save_path", "./Plots/3D/3D_NSYS_ODE.html"),
        "background_color": threejs.get("background_color", "#ffffff"),
        "point_size": float(threejs.get("point_size", 2.0)),
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
        "save_path": animation.get(
            "poincare_animation_save", "./Plots/2D/poincare_animation.html"
        ),
        "max_animation_size": float(animation.get("max_animation_size", 64.0)),
    }


def get_poincare_plot_settings(config):
    poincare = config.get("poincare", {})
    return {
        "show_2d": bool(poincare.get("show_2d", True)),
        "show_3d": bool(poincare.get("show_3d", False)),
        "epsilon": float(poincare.get("epsilon", 1e-18)),
        "up_save_path": poincare.get("up_save_path", "./Plots/2D/poincare_plot_up.png"),
        "down_save_path": poincare.get(
            "down_save_path", "./Plots/2D/poincare_plot_down.png"
        ),
    }


def _plane_equation(plane, point):
    return plane[0] * point[0] + plane[1] * point[1] + plane[2] * point[2] + plane[3]


def compute_poincare_crossings(viewer, config):
    poincare = get_poincare_settings(config)
    if not poincare["enabled"]:
        return [], []

    projection_axes = get_plot_3d_settings(config)["projection_axes"]
    color_variable = get_plot_3d_settings(config)["color_by"]
    compute_boundary = get_integration_settings(config)["compute_boundary"]
    epsilon = get_poincare_plot_settings(config)["epsilon"]
    plane = poincare["plane"]

    upward_crossings = []
    downward_crossings = []

    for traj_idx, (sol, label) in enumerate(viewer.solutions):
        trajectory = sol.get_trajectory(compute_boundary=compute_boundary)
        for i in range(len(trajectory) - 1):
            p1 = trajectory[i]
            p2 = trajectory[i + 1]
            try:
                point1 = np.array(
                    [float(p1[projection_axes[j]]) for j in range(3)], dtype=float
                )
                point2 = np.array(
                    [float(p2[projection_axes[j]]) for j in range(3)], dtype=float
                )
            except Exception:
                continue

            h1 = _plane_equation(plane, point1)
            h2 = _plane_equation(plane, point2)
            point3d = None
            alpha = None

            if h1 * h2 < 0:
                alpha = -h1 / (h2 - h1)
                point3d = point1 + alpha * (point2 - point1)
            elif abs(h1) <= epsilon and abs(h2) > epsilon:
                alpha = 0.0
                point3d = point1
            elif abs(h2) <= epsilon and abs(h1) > epsilon:
                alpha = 1.0
                point3d = point2
            else:
                continue

            color_value = None
            if color_variable is not None:
                try:
                    color_value = float(
                        p1[color_variable]
                        + (alpha if alpha is not None else 0.0)
                        * (p2[color_variable] - p1[color_variable])
                    )
                except Exception:
                    color_value = None

            intersection = {
                "point3d": point3d,
                "color_value": color_value,
                "trajectory_index": traj_idx,
                "label": label,
            }

            if h1 < -epsilon and h2 > epsilon:
                upward_crossings.append(intersection)
            elif h1 > epsilon and h2 < -epsilon:
                downward_crossings.append(intersection)
            elif abs(h1) <= epsilon and h2 > epsilon:
                upward_crossings.append(intersection)
            elif abs(h1) <= epsilon and h2 < -epsilon:
                downward_crossings.append(intersection)
            elif abs(h2) <= epsilon and h1 < -epsilon:
                upward_crossings.append(intersection)
            elif abs(h2) <= epsilon and h1 > epsilon:
                downward_crossings.append(intersection)

    return upward_crossings, downward_crossings


def plot_poincare_sections(viewer, config):
    settings = get_poincare_plot_settings(config)
    if not settings["show_2d"]:
        print("Poincaré 2D plotting is disabled in config.")
        return None

    upward, downward = compute_poincare_crossings(viewer, config)
    plane = get_poincare_settings(config)["plane"]
    plot_settings = get_plot_3d_settings(config)

    if upward:
        print(f"Found {len(upward)} upward crossings")
        plot_poincare_section(
            upward,
            plane,
            figsize=plot_settings["figsize"],
            title="Poincaré Section (up)",
            save_path=settings["up_save_path"],
        )
    else:
        print("Found 0 upward crossings")

    if downward:
        print(f"Found {len(downward)} downward crossings")
        plot_poincare_section(
            downward,
            plane,
            figsize=plot_settings["figsize"],
            title="Poincaré Section (down)",
            save_path=settings["down_save_path"],
        )
    else:
        print("Found 0 downward crossings")

    return {"up": upward, "down": downward}


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
        return ODESystemND(
            system_func, system_settings["n_vars"], system_settings["var_names"]
        )

    if highest_derivative is None:
        raise ValueError(
            "A highest_derivative function is required for higher-order systems"
        )

    if system_settings["ode_order"] is None:
        raise ValueError("ode_order must be defined for higher-order systems")

    return ODESystemND.from_higher_order(
        highest_derivative,
        int(system_settings["ode_order"]),
        system_settings["var_names"],
    )


def solve_initial_conditions(config, system, initial_conditions):
    integration = get_integration_settings(config)
    t_eval = np.linspace(
        integration["t_start"], integration["t_end"], integration["num_points"]
    )
    viewer = ODEViewerND()
    viewer.solve_ics_grid(
        system,
        (integration["t_start"], integration["t_end"]),
        initial_conditions,
        len(initial_conditions),
        t_eval=t_eval,
        max_step=integration["step_size"],
        show_progress=integration["show_progress"],
    )
    return viewer


def plot_phase_space(viewer, config):
    plot_3d = get_plot_3d_settings(config)
    save_path = plot_3d["save_path"] if plot_3d["save_plot"] else None
    return viewer.plot_all_3d(
        projection_axes=plot_3d["projection_axes"],
        color_variable=plot_3d["color_by"],
        colormap=plot_3d["colormap"],
        figsize=plot_3d["figsize"],
        title=plot_3d["title"],
        save_path=save_path,
        max_boundary=plot_3d["max_boundary"],
        compute_boundary=get_integration_settings(config)["compute_boundary"],
    )


def _build_threejs_html(trajectories, title, background_color, line_width):
    return f"""<!DOCTYPE html>
<html lang=\"en\">
<head>
<meta charset=\"utf-8\"/>
<title>{title}</title>
<script src=\"https://cdnjs.cloudflare.com/ajax/libs/three.js/r150/three.min.js\"></script>
<script src=\"https://cdn.jsdelivr.net/npm/three@0.150.1/examples/js/controls/OrbitControls.js\"></script>
<style>
  body {{ margin: 0; overflow: hidden; background: {background_color}; }}
  #container {{ width: 100vw; height: 100vh; }}
</style>
</head>
<body>
<div id=\"container\"></div>
<script>
const data = {json.dumps(trajectories)};
const container = document.getElementById('container');
const scene = new THREE.Scene();
scene.background = new THREE.Color('{background_color}');
const camera = new THREE.PerspectiveCamera(45, window.innerWidth / window.innerHeight, 0.1, 1000);
const renderer = new THREE.WebGLRenderer({{ antialias: true }});
renderer.setPixelRatio(window.devicePixelRatio);
renderer.setSize(window.innerWidth, window.innerHeight);
container.appendChild(renderer.domElement);
const controls = new THREE.OrbitControls(camera, renderer.domElement);
controls.target.set(0, 0, 0);
controls.update();
const ambient = new THREE.AmbientLight(0xffffff, 0.7);
scene.add(ambient);
const directional = new THREE.DirectionalLight(0xffffff, 0.8);
directional.position.set(5, 10, 7);
scene.add(directional);
const axes = new THREE.AxesHelper(5);
scene.add(axes);
function makeColor(traj) {{
  if (traj.normalized_colors && traj.normalized_colors.length > 0) {{
    return new THREE.Color().setHSL(traj.normalized_colors[0], 0.7, 0.5);
  }}
  return new THREE.Color().setHSL(traj.trajectory_color || 0.5, 0.7, 0.5);
}}
function loadTrajectory(traj) {{
  const points = traj.points.map(p => new THREE.Vector3(p[0], p[1], p[2]));
  const geometry = new THREE.BufferGeometry().setFromPoints(points);
  const material = new THREE.LineBasicMaterial({{ color: makeColor(traj), linewidth: Math.max(1, {line_width}) }});
  const line = new THREE.Line(geometry, material);
  scene.add(line);
}}
data.forEach(loadTrajectory);
function animate() {{
  requestAnimationFrame(animate);
  controls.update();
  renderer.render(scene, camera);
}}
window.addEventListener('resize', () => {{
  camera.aspect = window.innerWidth / window.innerHeight;
  camera.updateProjectionMatrix();
  renderer.setSize(window.innerWidth, window.innerHeight);
}});
camera.position.set(10, 10, 10);
animate();
</script>
</body>
</html>"""


def plot_threejs(viewer, config):
    threejs = get_threejs_settings(config)
    if not threejs["enabled"]:
        print("Three.js export is disabled in config.")
        return None

    projection_axes = get_plot_3d_settings(config)["projection_axes"]
    color_variable = get_plot_3d_settings(config)["color_by"]
    compute_boundary = get_integration_settings(config)["compute_boundary"]

    trajectories = viewer.get_threejs_trajectories(
        projection_axes=projection_axes,
        color_variable=color_variable,
        compute_boundary=compute_boundary,
    )

    save_path = threejs["save_path"]
    save_dir = os.path.dirname(save_path)
    if save_dir:
        os.makedirs(save_dir, exist_ok=True)

    html = _build_threejs_html(
        trajectories,
        "Interactive 3D Trajectories",
        threejs["background_color"],
        threejs["point_size"],
    )

    with open(save_path, "w", encoding="utf-8") as f:
        f.write(html)

    print(f"Saved Three.js plot to: {save_path}")
    return save_path


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
    plt.rcParams["animation.embed_limit"] = animation["max_animation_size"]
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
