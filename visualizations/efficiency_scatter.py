"""
Efficiency scatter plot visualizations.
Implements Figures 2, 5, 6, 8, 9 from the paper.
"""

import matplotlib.pyplot as plt
import numpy as np
from typing import List, Dict, Tuple, Optional

from .style_config import (
    PAPER_COLORS, FIGURE_SIZES, FONT_SIZES, MARKER_STYLES,
    apply_paper_style, add_diagonal_line, add_percentage_legend
)
from .utils import compare_efficiencies, calculate_percentages


def plot_efficiency_scatter(
    x_efficiencies: List[float],
    y_efficiencies: List[float],
    x_label: str = 'Spending Efficiency of MES',
    y_label: str = 'Spending Efficiency of EES',
    title: str = 'Comparing EES and MES',
    show_percentages: bool = True,
    percentage_labels: Dict[str, str] = None,
    figsize: Tuple[float, float] = None,
    ax: plt.Axes = None
) -> plt.Figure:
    """
    Create an efficiency comparison scatter plot.

    Args:
        x_efficiencies: Efficiency values for x-axis (e.g., MES)
        y_efficiencies: Efficiency values for y-axis (e.g., EES)
        x_label: Label for x-axis
        y_label: Label for y-axis
        title: Plot title
        show_percentages: Whether to show percentage breakdown
        percentage_labels: Custom labels for percentage box
        figsize: Figure size
        ax: Existing axes to plot on

    Returns:
        Matplotlib Figure object
    """
    if figsize is None:
        figsize = FIGURE_SIZES['scatter']

    if ax is None:
        fig, ax = plt.subplots(figsize=figsize)
    else:
        fig = ax.get_figure()

    # Convert to numpy arrays
    x = np.array(x_efficiencies)
    y = np.array(y_efficiencies)

    # Create scatter plot
    ax.scatter(x, y, c=PAPER_COLORS['mes'],
               s=MARKER_STYLES['scatter_size'],
               alpha=MARKER_STYLES['scatter_alpha'],
               edgecolors='white', linewidths=0.5)

    # Apply styling
    apply_paper_style(ax, title=title, xlabel=x_label, ylabel=y_label)

    # Add diagonal reference line
    add_diagonal_line(ax, color=PAPER_COLORS['diagonal'])

    # Calculate and display percentages
    if show_percentages:
        comparisons = [compare_efficiencies(xi, yi) for xi, yi in zip(x, y)]
        percentages = calculate_percentages(comparisons)

        if percentage_labels is None:
            percentage_labels = {
                'first': 'MES',
                'equal': 'Equal',
                'second': 'EES'
            }

        add_percentage_legend(ax, percentages, percentage_labels)

    # Set axis limits
    min_val = min(x.min(), y.min()) - 0.05
    max_val = max(x.max(), y.max()) + 0.05
    ax.set_xlim(max(0.3, min_val), min(1.0, max_val))
    ax.set_ylim(max(0.3, min_val), min(1.0, max_val))

    plt.tight_layout()
    return fig


def plot_figure_2(
    data: Dict = None,
    figsize: Tuple[float, float] = None
) -> plt.Figure:
    """
    Create Figure 2: MES vs EES with ADD-ONE heuristic (cardinal and cost utilities).

    Args:
        data: Dictionary with 'cardinal' and 'cost' keys, each containing 'mes' and 'ees' lists
        figsize: Figure size

    Returns:
        Matplotlib Figure object
    """
    if figsize is None:
        figsize = FIGURE_SIZES['scatter_pair']

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=figsize)

    # Cardinal utilities (left)
    if data and 'cardinal' in data:
        mes_card = data['cardinal']['mes']
        ees_card = data['cardinal']['ees']
    else:
        # Default sample data
        from .sample_data import generate_comparison_data
        sample = generate_comparison_data()
        mes_card = sample['cardinal']['mes']
        ees_card = sample['cardinal']['ees']

    x = np.array(mes_card)
    y = np.array(ees_card)

    ax1.scatter(x, y, c=PAPER_COLORS['mes'],
                s=MARKER_STYLES['scatter_size'],
                alpha=MARKER_STYLES['scatter_alpha'],
                edgecolors='white', linewidths=0.5)

    apply_paper_style(ax1, title='Comparing EES and MES with Cardinal Utilities',
                       xlabel='Spending Efficiency of MES',
                       ylabel='Spending Efficiency of EES')
    add_diagonal_line(ax1)

    comparisons = [compare_efficiencies(xi, yi) for xi, yi in zip(x, y)]
    percentages = calculate_percentages(comparisons)
    add_percentage_legend(ax1, percentages, {'first': 'MES', 'equal': 'Equal', 'second': 'EES'})

    # Cost utilities (right)
    if data and 'cost' in data:
        mes_cost = data['cost']['mes']
        ees_cost = data['cost']['ees']
    else:
        mes_cost = sample['cost']['mes']
        ees_cost = sample['cost']['ees']

    x = np.array(mes_cost)
    y = np.array(ees_cost)

    ax2.scatter(x, y, c=PAPER_COLORS['mes'],
                s=MARKER_STYLES['scatter_size'],
                alpha=MARKER_STYLES['scatter_alpha'],
                edgecolors='white', linewidths=0.5)

    apply_paper_style(ax2, title='Comparing EES and MES with Cost Utilities',
                       xlabel='Spending Efficiency of MES',
                       ylabel='Spending Efficiency of EES')
    add_diagonal_line(ax2)

    comparisons = [compare_efficiencies(xi, yi) for xi, yi in zip(x, y)]
    percentages = calculate_percentages(comparisons)
    add_percentage_legend(ax2, percentages, {'first': 'MES', 'equal': 'Equal', 'second': 'EES'})

    # Label subplots
    ax1.text(-0.1, 1.05, '(a)', transform=ax1.transAxes,
             fontsize=12, fontweight='bold', va='bottom')
    ax2.text(-0.1, 1.05, '(b)', transform=ax2.transAxes,
             fontsize=12, fontweight='bold', va='bottom')

    plt.tight_layout()
    return fig


def plot_figures_5_6(
    data: Dict = None,
    figsize: Tuple[float, float] = None
) -> Tuple[plt.Figure, plt.Figure]:
    """
    Create Figures 5 and 6: EES ADD-OPT-SKIP vs MES ADD-ONE.

    Args:
        data: Dictionary with efficiency data
        figsize: Figure size for each figure

    Returns:
        Tuple of two Matplotlib Figure objects (cardinal, cost)
    """
    if figsize is None:
        figsize = FIGURE_SIZES['scatter']

    if data is None:
        from .sample_data import generate_add_opt_skip_comparison_data
        data = generate_add_opt_skip_comparison_data()

    # Figure 5: Cardinal utilities
    fig5, ax5 = plt.subplots(figsize=figsize)
    x = np.array(data['cardinal']['mes'])
    y = np.array(data['cardinal']['ees'])

    ax5.scatter(x, y, c=PAPER_COLORS['mes'],
                s=MARKER_STYLES['scatter_size'],
                alpha=MARKER_STYLES['scatter_alpha'],
                edgecolors='white', linewidths=0.5)

    apply_paper_style(ax5, title='Spending efficiency of EES with ADD-\nOPT-SKIP vs. MES with ADD-ONE: cardinal utilities.',
                       xlabel='Spending Efficiency of MES',
                       ylabel='Spending Efficiency of EES')
    add_diagonal_line(ax5)

    comparisons = [compare_efficiencies(xi, yi) for xi, yi in zip(x, y)]
    percentages = calculate_percentages(comparisons)
    add_percentage_legend(ax5, percentages, {'first': 'MES', 'equal': 'Equal', 'second': 'EES'})

    plt.tight_layout()

    # Figure 6: Cost utilities
    fig6, ax6 = plt.subplots(figsize=figsize)
    x = np.array(data['cost']['mes'])
    y = np.array(data['cost']['ees'])

    ax6.scatter(x, y, c=PAPER_COLORS['mes'],
                s=MARKER_STYLES['scatter_size'],
                alpha=MARKER_STYLES['scatter_alpha'],
                edgecolors='white', linewidths=0.5)

    apply_paper_style(ax6, title='Spending efficiency of EES with ADD-\nOPT-SKIP vs. MES with ADD-ONE: cost utilities.',
                       xlabel='Spending Efficiency of MES',
                       ylabel='Spending Efficiency of EES')
    add_diagonal_line(ax6)

    comparisons = [compare_efficiencies(xi, yi) for xi, yi in zip(x, y)]
    percentages = calculate_percentages(comparisons)
    add_percentage_legend(ax6, percentages, {'first': 'MES', 'equal': 'Equal', 'second': 'EES'})

    plt.tight_layout()

    return fig5, fig6


def plot_figures_8_9(
    data: Dict = None,
    figsize: Tuple[float, float] = None
) -> Tuple[plt.Figure, plt.Figure]:
    """
    Create Figures 8 and 9: Raw MES vs EES comparison (no completion methods).

    Args:
        data: Dictionary with raw efficiency data
        figsize: Figure size for each figure

    Returns:
        Tuple of two Matplotlib Figure objects (cardinal, cost)
    """
    if figsize is None:
        figsize = FIGURE_SIZES['scatter']

    if data is None:
        from .sample_data import generate_raw_comparison_data
        data = generate_raw_comparison_data()

    # Figure 8: Cardinal utilities
    fig8, ax8 = plt.subplots(figsize=figsize)
    x = np.array(data['cardinal']['mes'])
    y = np.array(data['cardinal']['ees'])

    ax8.scatter(x, y, c=PAPER_COLORS['mes'],
                s=MARKER_STYLES['scatter_size'],
                alpha=MARKER_STYLES['scatter_alpha'],
                edgecolors='white', linewidths=0.5)

    apply_paper_style(ax8, title='Comparing EES and MES with Cardinal Utilities',
                       xlabel='Spending Efficiency of MES',
                       ylabel='Spending Efficiency of EES')
    add_diagonal_line(ax8)

    comparisons = [compare_efficiencies(xi, yi) for xi, yi in zip(x, y)]
    percentages = calculate_percentages(comparisons)
    add_percentage_legend(ax8, percentages, {'first': 'MES', 'equal': 'Equal', 'second': 'EES'})

    # Adjust axis for lower efficiency values
    ax8.set_xlim(0.1, 0.8)
    ax8.set_ylim(0.1, 0.8)

    plt.tight_layout()

    # Figure 9: Cost utilities
    fig9, ax9 = plt.subplots(figsize=figsize)
    x = np.array(data['cost']['mes'])
    y = np.array(data['cost']['ees'])

    ax9.scatter(x, y, c=PAPER_COLORS['mes'],
                s=MARKER_STYLES['scatter_size'],
                alpha=MARKER_STYLES['scatter_alpha'],
                edgecolors='white', linewidths=0.5)

    apply_paper_style(ax9, title='Comparing EES and MES with Cost Utilities',
                       xlabel='Spending Efficiency of MES',
                       ylabel='Spending Efficiency of EES')
    add_diagonal_line(ax9)

    comparisons = [compare_efficiencies(xi, yi) for xi, yi in zip(x, y)]
    percentages = calculate_percentages(comparisons)
    add_percentage_legend(ax9, percentages, {'first': 'MES', 'equal': 'Equal', 'second': 'EES'})

    ax9.set_xlim(0.1, 0.9)
    ax9.set_ylim(0.1, 0.9)

    plt.tight_layout()

    return fig8, fig9


def create_all_scatter_figures(data: Dict = None) -> Dict[str, plt.Figure]:
    """
    Create all scatter plot figures.

    Args:
        data: Optional data dictionary with all required data

    Returns:
        Dictionary mapping figure names to Figure objects
    """
    figures = {}

    # Figure 2
    fig2_data = data.get('figure_2') if data else None
    figures['figure_2'] = plot_figure_2(fig2_data)

    # Figures 5 and 6
    fig5_6_data = data.get('figures_5_6') if data else None
    figures['figure_5'], figures['figure_6'] = plot_figures_5_6(fig5_6_data)

    # Figures 8 and 9
    fig8_9_data = data.get('figures_8_9') if data else None
    figures['figure_8'], figures['figure_9'] = plot_figures_8_9(fig8_9_data)

    return figures
