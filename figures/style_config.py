"""
Style configuration for paper visualizations.
Defines colors, fonts, figure sizes to match the paper's figures.
"""

import matplotlib.pyplot as plt
import matplotlib as mpl
from typing import List, Dict, Optional
import numpy as np

# Color scheme matching the paper
PAPER_COLORS = {
    # Method comparison colors
    'mes': '#1f77b4',           # Blue for MES
    'ees': '#ff7f0e',           # Orange for EES
    'equal': '#2ca02c',         # Green for equal
    'max': '#d62728',           # Red for MAX

    # Bar chart colors
    'cost': '#d62728',          # Red for cost utilities
    'cardinal': '#1f77b4',      # Blue for cardinal utilities

    # Reference lines
    'reference_line': '#666666',
    'diagonal': '#888888',

    # Project colors for timeline (will be generated dynamically)
    'project_palette': [
        '#e41a1c', '#377eb8', '#4daf4a', '#984ea3',
        '#ff7f00', '#ffff33', '#a65628', '#f781bf',
        '#999999', '#66c2a5', '#fc8d62', '#8da0cb'
    ]
}

# Figure sizes matching paper layout
FIGURE_SIZES = {
    'scatter': (6, 5),
    'scatter_pair': (12, 5),       # Two scatter plots side by side
    'bars': (10, 5),
    'bars_pair': (14, 5),          # Two bar charts side by side
    'trajectory': (12, 5),         # Efficiency + project selection
    'histogram_quad': (10, 8),     # 2x2 grid of histograms
    'single_histogram': (6, 4),
}

# Font sizes
FONT_SIZES = {
    'title': 12,
    'axis_label': 10,
    'tick_label': 9,
    'legend': 9,
    'annotation': 9,
    'percentage_box': 10,
}

# Line styles
LINE_STYLES = {
    'efficiency': '-',
    'reference': '--',
    'diagonal': '-',
}

# Marker styles
MARKER_STYLES = {
    'scatter': 'o',
    'scatter_size': 30,
    'scatter_alpha': 0.6,
}


def apply_paper_style(ax: plt.Axes, title: str = None,
                       xlabel: str = None, ylabel: str = None) -> None:
    """
    Apply consistent paper styling to an axis.

    Args:
        ax: Matplotlib axis object
        title: Optional title for the plot
        xlabel: Optional x-axis label
        ylabel: Optional y-axis label
    """
    # Set spine visibility
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)

    # Set grid
    ax.grid(True, alpha=0.3, linestyle='-', linewidth=0.5)

    # Set labels if provided
    if title:
        ax.set_title(title, fontsize=FONT_SIZES['title'], fontweight='bold')
    if xlabel:
        ax.set_xlabel(xlabel, fontsize=FONT_SIZES['axis_label'])
    if ylabel:
        ax.set_ylabel(ylabel, fontsize=FONT_SIZES['axis_label'])

    # Set tick label sizes
    ax.tick_params(axis='both', labelsize=FONT_SIZES['tick_label'])


def get_project_colors(project_names: List[str]) -> Dict[str, str]:
    """
    Generate consistent colors for project names.

    Args:
        project_names: List of project names/IDs

    Returns:
        Dictionary mapping project names to colors
    """
    colors = {}
    palette = PAPER_COLORS['project_palette']

    for i, name in enumerate(project_names):
        colors[name] = palette[i % len(palette)]

    return colors


def add_diagonal_line(ax: plt.Axes, color: str = None,
                       linestyle: str = '--', alpha: float = 0.5) -> None:
    """
    Add a diagonal reference line (y=x) to a scatter plot.

    Args:
        ax: Matplotlib axis object
        color: Line color
        linestyle: Line style
        alpha: Line transparency
    """
    if color is None:
        color = PAPER_COLORS['diagonal']

    lims = [
        np.min([ax.get_xlim(), ax.get_ylim()]),
        np.max([ax.get_xlim(), ax.get_ylim()]),
    ]
    ax.plot(lims, lims, linestyle=linestyle, color=color, alpha=alpha, zorder=0)
    ax.set_xlim(lims)
    ax.set_ylim(lims)


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


def add_100_percent_line(ax: plt.Axes, orientation: str = 'horizontal',
                          value: float = 1.0, label: str = '100% SE') -> None:
    """
    Add a 100% spending efficiency reference line.

    Args:
        ax: Matplotlib axis object
        orientation: 'horizontal' or 'vertical'
        value: Value at which to draw the line
        label: Label for the line
    """
    color = PAPER_COLORS['reference_line']

    if orientation == 'horizontal':
        ax.axhline(y=value, color=color, linestyle='--', alpha=0.7, label=label)
    else:
        ax.axvline(x=value, color=color, linestyle='--', alpha=0.7, label=label)


def create_figure_with_subplots(nrows: int, ncols: int,
                                  figsize: tuple = None,
                                  **kwargs) -> tuple:
    """
    Create a figure with subplots using paper styling.

    Args:
        nrows: Number of rows
        ncols: Number of columns
        figsize: Figure size tuple
        **kwargs: Additional arguments for plt.subplots

    Returns:
        Tuple of (figure, axes)
    """
    if figsize is None:
        figsize = (6 * ncols, 5 * nrows)

    fig, axes = plt.subplots(nrows, ncols, figsize=figsize, **kwargs)

    # Set figure background
    fig.patch.set_facecolor('white')

    return fig, axes


def setup_log_scale(ax: plt.Axes, axis: str = 'both') -> None:
    """
    Setup logarithmic scale for an axis.

    Args:
        ax: Matplotlib axis object
        axis: 'x', 'y', or 'both'
    """
    if axis in ['x', 'both']:
        ax.set_xscale('log')
    if axis in ['y', 'both']:
        ax.set_yscale('log')


def format_budget_axis(ax: plt.Axes, axis: str = 'x',
                        currency: str = 'PLN') -> None:
    """
    Format budget values on an axis with appropriate labels.

    Args:
        ax: Matplotlib axis object
        axis: 'x' or 'y'
        currency: Currency label
    """
    def formatter(x, pos):
        if x >= 1e6:
            return f'{x/1e6:.1f}M'
        elif x >= 1e3:
            return f'{x/1e3:.0f}K'
        else:
            return f'{x:.0f}'

    if axis == 'x':
        ax.xaxis.set_major_formatter(plt.FuncFormatter(formatter))
        ax.set_xlabel(f'Budget ({currency}, log scale)')
    else:
        ax.yaxis.set_major_formatter(plt.FuncFormatter(formatter))
        ax.set_ylabel(f'Budget ({currency}, log scale)')


def add_correlation_annotation(ax: plt.Axes, corr: float,
                                 loc: str = 'upper right') -> None:
    """
    Add correlation annotation to a scatter plot.

    Args:
        ax: Matplotlib axis object
        corr: Correlation coefficient
        loc: Location for annotation
    """
    if loc == 'upper right':
        x, y = 0.95, 0.95
        ha, va = 'right', 'top'
    else:
        x, y = 0.05, 0.95
        ha, va = 'left', 'top'

    ax.text(x, y, f'Corr: {corr:.2f}',
            transform=ax.transAxes,
            fontsize=FONT_SIZES['annotation'],
            horizontalalignment=ha,
            verticalalignment=va,
            bbox=dict(boxstyle='round', facecolor='white', alpha=0.8))


def add_percentile_lines(ax: plt.Axes, percentiles: Dict[int, float],
                          orientation: str = 'vertical') -> None:
    """
    Add percentile reference lines to a histogram.

    Args:
        ax: Matplotlib axis object
        percentiles: Dict mapping percentile to value (e.g., {25: 750, 50: 1601})
        orientation: 'vertical' or 'horizontal'
    """
    colors = ['#ff7f0e', '#2ca02c', '#d62728', '#9467bd']

    for i, (pct, val) in enumerate(percentiles.items()):
        color = colors[i % len(colors)]
        if orientation == 'vertical':
            ax.axvline(x=val, color=color, linestyle='--', alpha=0.7,
                        label=f'{pct}th: {val:,.0f}')
        else:
            ax.axhline(y=val, color=color, linestyle='--', alpha=0.7,
                        label=f'{pct}th: {val:,.0f}')
