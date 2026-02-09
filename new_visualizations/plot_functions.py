import numpy as np
import matplotlib.pyplot as plt
from typing import List, Dict, Tuple

from utils import calculate_percentages, compare_efficiencies
from style_config import PAPER_COLORS,FIGURE_SIZES, FONT_SIZES, MARKER_STYLES, apply_paper_style

def add_percentage_legend(ax: plt.Axes, percentages: Dict[str, float],
                           labels: Dict[str, str], loc: str = 'upper left') -> None:
    """
    Add a percentage breakdown legend box to a plot.

    Args:
        ax: Matplotlib axis object
        percentages: Dict with percentage values (e.g., {'mes': 14.74, 'equal': 72.51, 'ees': 12.75})
        labels: Dict mapping keys to display labels
        loc: Legend location
    """
    text_lines = []
    for key, label in labels.items():
        if key in percentages:
            text_lines.append(f"{label}: {percentages[key]:.2f}%")

    text = '\n'.join(text_lines)

    props = dict(boxstyle='round', facecolor='white', alpha=0.8, edgecolor='gray')
    ax.text(0.02, 0.98, text, transform=ax.transAxes,
            fontsize=FONT_SIZES['percentage_box'],
            verticalalignment='top', bbox=props)

def comparison_scatter_plot(
    x1: List[float],
    y1: List[float],
    x2: List[float],
    y2: List[float],
    x_label: str = 'Spending Efficiency of MES',
    y_label: str = 'Spending Efficiency of EES',
    title1: str = 'Cardinal Utilities',
    title2: str = 'Cost Utilities',
    show_percentages: bool = True,
    percentage_labels: Dict[str, str] = None,
    figsize: Tuple[float, float] = None
) -> plt.Figure:
    """
    Create side-by-side efficiency comparison scatter plots for cardinal and cost utilities.

    Args:
        x1: Values for x-axis (cardinal)
        y1: Values for y-axis (cardinal)
        x2: Values for x-axis (cost)
        y2: Values for y-axis (cost)
        x_label: Label for x-axis
        y_label: Label for y-axis
        title: Plot title
        show_percentages: Whether to show percentage breakdown
        percentage_labels: Custom labels for percentage box, e.g. {'first': 'EES', 'equal': 'Equal', 'second': 'MES'}
        figsize: Figure size
    Returns:
        Matplotlib Figure object
    """
    def plot_single(ax: plt.Axes, x_vals, y_vals, plot_title: str):
        x_arr = np.array(x_vals)
        y_arr = np.array(y_vals)

        ax.scatter(x_arr, y_arr,
               s=MARKER_STYLES['scatter_size'],
               alpha=MARKER_STYLES['scatter_alpha'],
               edgecolors='white', linewidths=0.5)

        apply_paper_style(ax, title=plot_title, xlabel=x_label, ylabel=y_label)

        lims = [
            np.min([ax.get_xlim(), ax.get_ylim()]),
            np.max([ax.get_xlim(), ax.get_ylim()]),
        ]
        ax.plot(lims, lims, linestyle='--', color=PAPER_COLORS['diagonal'], alpha=0.5, zorder=0)
        ax.set_xlim(lims)
        ax.set_ylim(lims)

        if show_percentages:
            comparisons = [compare_efficiencies(xi, yi) for xi, yi in zip(x_arr, y_arr)]
            percentages = calculate_percentages(comparisons)
            add_percentage_legend(ax, percentages, percentage_labels)

        min_val = min(x_arr.min(), y_arr.min()) - 0.05
        max_val = max(x_arr.max(), y_arr.max()) + 0.05
        ax.set_xlim(max(0.3, min_val), min(1.0, max_val))
        ax.set_ylim(max(0.3, min_val), min(1.0, max_val))

    if figsize is None:
        figsize = FIGURE_SIZES['scatter']

    fig, axes = plt.subplots(1, 2, figsize=(figsize[0] * 2, figsize[1]))
    plot_single(axes[0], x1, y1, title1)
    plot_single(axes[1], x2, y2, title2)

    plt.tight_layout()
    return fig
