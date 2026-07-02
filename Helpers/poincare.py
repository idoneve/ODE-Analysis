import numpy as np
import matplotlib.pyplot as plt


def normalize_plane(plane):
    a, b, c, d = plane
    normal = np.array([a, b, c], dtype=float)
    norm = np.linalg.norm(normal)
    if norm == 0:
        raise ValueError("Plane normal cannot be zero")
    normal /= norm
    return (normal[0], normal[1], normal[2], d / norm)


def plane_basis(plane):
    a, b, c, d = normalize_plane(plane)
    normal = np.array([a, b, c], dtype=float)
    if abs(normal[0]) < 0.9:
        vref = np.array([1.0, 0.0, 0.0])
    else:
        vref = np.array([0.0, 1.0, 0.0])

    u_axis = vref - np.dot(vref, normal) * normal
    u_axis /= np.linalg.norm(u_axis)
    v_axis = np.cross(normal, u_axis)
    v_axis /= np.linalg.norm(v_axis)
    ref_point = -d * normal
    return normal, u_axis, v_axis, ref_point


def point3d_to_plane_coords(point3d, plane):
    _, u_axis, v_axis, ref_point = plane_basis(plane)
    vec = np.array(point3d, dtype=float) - ref_point
    return np.dot(vec, u_axis), np.dot(vec, v_axis)


def plot_poincare_section(
    intersection_points,
    plane,
    figsize=(6, 6),
    title=None,
    save_path=None,
    clamp_colors=True,
    show=True,
):
    if not intersection_points:
        print("No Poincaré points to plot.")
        return

    coords = [point3d_to_plane_coords(p["point3d"], plane) for p in intersection_points]
    x_vals, y_vals = zip(*coords)
    color_vals = [p["color_value"] for p in intersection_points]

    plt.figure(figsize=figsize)
    if any(cv is not None for cv in color_vals):
        valid = [cv for cv in color_vals if cv is not None]
        norm = plt.Normalize(vmin=min(valid), vmax=max(valid))
        colors = [plt.cm.viridis(norm(cv)) if cv is not None else (0.5, 0.5, 0.5, 1.0) for cv in color_vals]
    else:
        colors = "C0"

    plt.scatter(x_vals, y_vals, s=40, c=colors, edgecolors="black", linewidths=0.3)
    plt.xlabel("plane x")
    plt.ylabel("plane y")
    if title:
        plt.title(title)
    plt.grid(True, alpha=0.4)
    plt.tight_layout()
    if save_path:
        plt.savefig(save_path, dpi=150, bbox_inches="tight")
        print(f"Saved Poincaré section plot to: {save_path}")
    if show:
        plt.show()


def split_crossings(intersections, plane):
    # In some cases the direction of the crossing is implicit.
    # This helper can be extended if the input data includes sign/orientation.
    return intersections, []


def interpolate_plane(start_plane, end_plane, alpha):
    start_plane = normalize_plane(start_plane)
    end_plane = normalize_plane(end_plane)
    n0 = np.array(start_plane[:3], dtype=float)
    n1 = np.array(end_plane[:3], dtype=float)
    n = (1.0 - alpha) * n0 + alpha * n1
    norm = np.linalg.norm(n)
    if norm < 1e-12:
        n = n0
        norm = np.linalg.norm(n)
    n /= norm
    d = (1.0 - alpha) * start_plane[3] + alpha * end_plane[3]
    return (n[0], n[1], n[2], d)
