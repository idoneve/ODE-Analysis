from .poincare import interpolate_plane


def save_poincare_animation(
    viewer,
    start_plane,
    end_plane,
    projection_axes,
    duration=15,
    fps=24,
    trail_length=3,
    compute_boundary=None,
    color_variable=None,
    figsize=(7, 7),
    save_path=None,
):
    return viewer.animate_poincare_section(
        start_plane=start_plane,
        end_plane=end_plane,
        projection_axes=projection_axes,
        duration=duration,
        fps=fps,
        trail_length=trail_length,
        compute_boundary=compute_boundary,
        color_variable=color_variable,
        figsize=figsize,
        save_path=save_path,
    )
