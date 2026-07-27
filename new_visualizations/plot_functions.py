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
            verticalalignment='top', bbox=props)

def comparison_scatter_plot(
    x: List[float],
    y: List[float],
    x_label: str = 'Spending Efficiency of MES',
    y_label: str = 'Spending Efficiency of EES',
    title: str = '',
    show_percentages: bool = True,
    percentage_labels: Dict[str, str] = None,
    figsize: Tuple[float, float] = None
) -> plt.Figure:
    """
    Create an efficiency comparison scatter plot.

    Args:
        x: Values for x-axis
        y: Values for y-axis
        x_label: Label for x-axis
        y_label: Label for y-axis
        title: Plot title
        show_percentages: Whether to show percentage breakdown
        percentage_labels: Custom labels for percentage box, e.g. {'first': 'EES', 'equal': 'Equal', 'second': 'MES'}
        figsize: Figure size
    Returns:
        Matplotlib Figure object
    """
    if figsize is None:
        figsize = FIGURE_SIZES['scatter']

    fig, ax = plt.subplots(figsize=figsize)

    x_arr = np.array(x)
    y_arr = np.array(y)

    ax.scatter(x_arr, y_arr,
               s=MARKER_STYLES['scatter_size'],
               alpha=MARKER_STYLES['scatter_alpha'],
               edgecolors='white', linewidths=0.5)

    apply_paper_style(ax, title=title, xlabel=x_label, ylabel=y_label)

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

    fig.tight_layout()
    return fig

