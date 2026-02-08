"""
Style configuration for paper visualizations.
Defines colors, fonts, figure sizes for the paper
"""

import matplotlib.pyplot as plt

PAPER_COLORS = {
    'scatter': 'blue',
    'diagonal': 'grey'
}

FIGURE_SIZES = {
    'scatter': (6, 5),
}

FONT_SIZES = {
    'title': 12,
    'axis_label': 10,
    'tick_label': 9,
    'legend': 9,
    'annotation': 9,
    'percentage_box': 10,
}

LINE_STYLES = {
    'efficiency': '-',
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