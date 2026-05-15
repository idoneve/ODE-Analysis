import numpy as np
import matplotlib.pyplot as plt
from scipy.integrate import solve_ivp
import matplotlib.cm as cm


class ODESystemND:
    def __init__(self, system_func, n_vars, var_names=None):
        self.system_func = system_func
        self.n_vars = n_vars
        self.var_names = var_names or [f"x_{i}" for i in range(n_vars)]

    def solve(self, t_span, initial_state, t_eval=None, **kwargs):
        if len(initial_state) != self.n_vars:
            raise ValueError(f"Initial state must have {self.n_vars} variables")

        sol = solve_ivp(
            self.system_func, t_span, initial_state, t_eval=t_eval, **kwargs
        )
        return ODESolutionND(sol.t, sol.y, self.var_names)

    @classmethod
    def from_higher_order(cls, highest_derivative_func, n, var_names=None):
        def system(t, state):
            # state = [x, dx/dt, d²x/dt², ..., dⁿx/dtⁿ]
            derivatives = []
            # First order ODE: dx/dt, d²x/dt², ...
            for i in range(n - 1):
                derivatives.append(state[i + 1])
            # Highest derivative: dⁿx/dtⁿ
            derivatives.append(highest_derivative_func(t, state))
            return derivatives

        default_names = ["x"] + [f"x^{i}" for i in range(1, n)]
        var_names = var_names or default_names

        return cls(system, n, var_names)


class ODESolutionND:
    def __init__(self, t, y, var_names):
        self.t = t
        self.y = y  # shape: (n_vars, n_time_points)
        self.n_vars = len(y)
        self.var_names = var_names

    def get_trajectory(self):
        n_points = len(self.t)
        trajectory = []
        for i in range(n_points):
            point = [self.t[i]]
            point.extend([self.y[j][i] for j in range(self.n_vars)])
            trajectory.append(point)
        return trajectory

    def _get_variable_label(self, index):
        if index is None:
            return None
        if not isinstance(index, int):
            raise TypeError("color_variable and projection_axes values must be integers")
        if index < 0 or index >= self.n_vars + 1:
            raise ValueError(
                f"Index {index} is out of bounds. Use 0 for time or 1..{self.n_vars} for variables."
            )
        return "time" if index == 0 else self.var_names[index - 1]

    def project_to_3d(self, projection_axes=None, color_variable=None):
        if projection_axes is None:
            projection_axes = [0, 1, 2]  # t, x1, x2

        if len(projection_axes) != 3:
            raise ValueError("projection_axes must have exactly 3 indices")

        for axis in projection_axes:
            if not isinstance(axis, int):
                raise TypeError("projection_axes values must be integers")
            if axis < 0 or axis >= self.n_vars + 1:
                raise ValueError(
                    f"Projection axis {axis} is out of bounds. Use 0 for time or 1..{self.n_vars} for variables."
                )

        if color_variable is not None:
            if not isinstance(color_variable, int):
                raise TypeError("color_variable must be an integer")
            if color_variable < 0 or color_variable >= self.n_vars + 1:
                raise ValueError(
                    f"color_variable {color_variable} is out of bounds. Use 0 for time or 1..{self.n_vars} for variables."
                )

        trajectory = self.get_trajectory()
        x_coords = []
        y_coords = []
        z_coords = []
        colors = []

        for point in trajectory:
            x_coords.append(point[projection_axes[0]])
            y_coords.append(point[projection_axes[1]])
            z_coords.append(point[projection_axes[2]])

            if color_variable is not None:
                colors.append(point[color_variable])

        return (
            np.array(x_coords),
            np.array(y_coords),
            np.array(z_coords),
            np.array(colors),
        )

    def plot_3d(
        self,
        projection_axes=None,
        color_variable=None,
        figsize=(10, 8),
        title=None,
        save_path=None,
    ):
        x, y, z, colors = self.project_to_3d(projection_axes, color_variable)

        fig = plt.figure(figsize=figsize)
        ax = fig.add_subplot(111, projection="3d")
        
        if color_variable is not None and len(colors) > 0:
            scatter = ax.scatter(x, y, z, c=colors, cmap="viridis", alpha=0.8, s=20)
            color_label = self._get_variable_label(color_variable)
            plt.colorbar(scatter, ax=ax, label=color_label)
            ax.plot(x, y, z, alpha=0.3, color="gray")
        else:
            ax.plot(x, y, z, "b-", alpha=0.8, linewidth=1.5)

        if projection_axes is None:
            ax.set_xlabel("t")
            ax.set_ylabel(self.var_names[0])
            ax.set_zlabel(self.var_names[1])
        else:
            axis_labels = ["t"] + self.var_names
            ax.set_xlabel(axis_labels[projection_axes[0]])
            ax.set_ylabel(axis_labels[projection_axes[1]])
            ax.set_zlabel(axis_labels[projection_axes[2]])

        if title:
            ax.set_title(title)

        plt.tight_layout()

        if save_path:
            plt.savefig(save_path, dpi=150, bbox_inches="tight")

        plt.show()
        return fig, ax


class ODEViewerND:
    def __init__(self):
        self.solutions = []

    def add_solution(self, solution, label=None):
        self.solutions.append((solution, label))

    def solve_ics_grid(self, system, t_span, ic_grid, t_eval=None, **kwargs):
        for idx, ic in enumerate(ic_grid):
            sol = system.solve(t_span, ic, t_eval=t_eval, **kwargs)
            self.add_solution(sol)

            print(f"Completed trajectory {idx + 1} of {len(ic)}")

    def plot_all_3d(
        self,
        projection_axes=None,
        color_variable=None,
        figsize=(12, 8),
        title=None,
        save_path=None,
    ):
        if not self.solutions:
            print("No solutions to plot.")
            return

        fig = plt.figure(figsize=figsize)
        ax = fig.add_subplot(111, projection="3d")
        
        if color_variable is None:
            colors = cm.viridis(np.linspace(0, 1, len(self.solutions)))

        for i, (sol, label) in enumerate(self.solutions):
            if color_variable is not None:
                x, y, z, color_values = sol.project_to_3d(projection_axes, color_variable)
                sc = ax.scatter(
                    x, y, z, c=color_values, cmap="viridis", alpha=0.7, s=2, label=label
                )
                if i == 0:
                    plt.colorbar(
                        sc,
                        ax=ax,
                        label=sol._get_variable_label(color_variable),
                    )
            else:
                x, y, z, _ = sol.project_to_3d(projection_axes, None)
                ax.plot(x, y, z, color=colors[i], alpha=0.7, linewidth=1, label=label)
        
        if projection_axes is None:
            ax.set_xlabel("t")
            ax.set_ylabel(sol.var_names[0])
            ax.set_zlabel(sol.var_names[1])
        else:
            var_names = ["t"] + sol.var_names
            ax.set_xlabel(var_names[projection_axes[0]])
            ax.set_ylabel(var_names[projection_axes[1]])
            ax.set_zlabel(var_names[projection_axes[2]])
        
        if title:
            ax.set_title(title)
        if label and color_variable is None:
            ax.legend()
        plt.tight_layout()
        if save_path:
            plt.savefig(save_path, dpi=150, bbox_inches="tight")
        plt.show()
        return fig, ax
