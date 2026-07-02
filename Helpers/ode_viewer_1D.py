import numpy as np
import matplotlib.pyplot as plt
from scipy.integrate import solve_ivp


def solve_scalar_ode(func, t_span, y0, t_eval=None, max_step=None, **kwargs):
    def rhs(t, y):
        return func(y[0], t)

    sol = solve_ivp(rhs, t_span, [y0], t_eval=t_eval, max_step=max_step, **kwargs)
    return sol.t, sol.y[0]


def compute_initial_conditions(xmin, xmax, ymin, ymax, num_sx, num_sy, exclude_zero=True):
    xs = np.linspace(xmin, xmax, num_sx)
    ys = np.linspace(ymin, ymax, num_sy)
    points = []
    for x in xs:
        for y in ys:
            if exclude_zero and np.isclose(x, 0.0) and np.isclose(y, 0.0):
                continue
            points.append([x, y])
    return points


def plot_solution_curves(
    solutions,
    xlabel="t",
    ylabel="x",
    title=None,
    figsize=(8, 6),
    save_path=None,
    show=True,
):
    plt.figure(figsize=figsize)
    for idx, (t, y) in enumerate(solutions):
        plt.plot(t, y, linewidth=1.2, alpha=0.8, label=f"traj_{idx + 1}")

    if title:
        plt.title(title)
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
    plt.grid(True, alpha=0.35)
    if len(solutions) > 1:
        plt.legend(fontsize=8)
    plt.tight_layout()
    if save_path:
        plt.savefig(save_path, dpi=150, bbox_inches="tight")
    if show:
        plt.show()


def plot_direction_field(func, x_range, y_range, grid=(20, 20), scale=1.0):
    xs = np.linspace(x_range[0], x_range[1], grid[0])
    ys = np.linspace(y_range[0], y_range[1], grid[1])
    X, Y = np.meshgrid(xs, ys)
    U = np.ones_like(X)
    V = func(X, Y)

    magnitudes = np.sqrt(U**2 + V**2)
    magnitudes[magnitudes == 0] = 1.0
    U = U / magnitudes * scale
    V = V / magnitudes * scale

    plt.quiver(X, Y, U, V, angles="xy", pivot="mid", alpha=0.75)
    plt.xlabel("t")
    plt.ylabel("x")
    plt.grid(True, alpha=0.35)
    plt.tight_layout()
