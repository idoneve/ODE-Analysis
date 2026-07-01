import numpy as np
import matplotlib.pyplot as plt
from scipy.integrate import solve_ivp


def solve_2d_system(system_func, t_span, initial_states, t_eval=None, max_step=None, **kwargs):
    solutions = []
    for state0 in initial_states:
        sol = solve_ivp(system_func, t_span, state0, t_eval=t_eval, max_step=max_step, **kwargs)
        solutions.append((sol.t, sol.y))
    return solutions


def plot_phase_portrait(
    solutions,
    projection=(0, 1),
    xlabel="x",
    ylabel="y",
    title=None,
    figsize=(8, 6),
    save_path=None,
    show=True,
):
    plt.figure(figsize=figsize)
    for idx, (t, y) in enumerate(solutions):
        xs = y[projection[0]]
        ys = y[projection[1]]
        plt.plot(xs, ys, linewidth=1.0, alpha=0.8, label=f"traj_{idx + 1}")

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


def plot_vector_field(fx, fy, x_range, y_range, grid=(20, 20), scale=1.0):
    xs = np.linspace(x_range[0], x_range[1], grid[0])
    ys = np.linspace(y_range[0], y_range[1], grid[1])
    X, Y = np.meshgrid(xs, ys)
    U = fx(X, Y)
    V = fy(X, Y)

    magnitudes = np.sqrt(U**2 + V**2)
    magnitudes[magnitudes == 0] = 1.0
    U = U / magnitudes * scale
    V = V / magnitudes * scale

    plt.figure(figsize=(8, 6))
    plt.quiver(X, Y, U, V, angles="xy", pivot="mid", alpha=0.75)
    plt.xlabel("x")
    plt.ylabel("y")
    plt.grid(True, alpha=0.35)
    plt.tight_layout()
    plt.show()
