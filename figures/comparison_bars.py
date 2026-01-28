"""
Comparison bar chart visualizations.
Implements Figures 3 and 4 from the paper.
"""

import matplotlib.pyplot as plt
import numpy as np
from typing import Dict, List, Tuple, Optional

from .style_config import (
    PAPER_COLORS, FIGURE_SIZES, FONT_SIZES,
    apply_paper_style
)


def plot_executions_comparison(
    data: Dict[str, Dict[str, float]],
    title: str = 'Executions Comparison',
    figsize: Tuple[float, float] = None,
    ax: plt.Axes = None
) -> plt.Figure:
    """
    Create a grouped bar chart comparing execution counts across methods.

    Args:
        data: Dictionary with method names as keys and
              {'cost': value, 'cardinal': value} as values
        title: Plot title
        figsize: Figure size
        ax: Existing axes to plot on

    Returns:
        Matplotlib Figure object
    """
    if figsize is None:
        figsize = (8, 5)

    if ax is None:
        fig, ax = plt.subplots(figsize=figsize)
    else:
        fig = ax.get_figure()

    methods = list(data.keys())
    n_methods = len(methods)

    # Extract values
    cost_values = [data[m].get('cost', 0) for m in methods]
    cardinal_values = [data[m].get('cardinal', 0) for m in methods]

    # Bar positions
    x = np.arange(n_methods)
    width = 0.35

    # Create bars
    bars1 = ax.bar(x - width/2, cost_values, width,
                   label='Cost', color=PAPER_COLORS['cost'], alpha=0.8)
    bars2 = ax.bar(x + width/2, cardinal_values, width,
                   label='Cardinal', color=PAPER_COLORS['cardinal'], alpha=0.8)

    # Add value labels on bars
    for bar in bars1:
        height = bar.get_height()
        ax.annotate(f'{int(height)}',
                    xy=(bar.get_x() + bar.get_width() / 2, height),
                    xytext=(0, 3),
                    textcoords="offset points",
                    ha='center', va='bottom',
                    fontsize=FONT_SIZES['annotation'])

    for bar in bars2:
        height = bar.get_height()
        ax.annotate(f'{int(height)}',
                    xy=(bar.get_x() + bar.get_width() / 2, height),
                    xytext=(0, 3),
                    textcoords="offset points",
                    ha='center', va='bottom',
                    fontsize=FONT_SIZES['annotation'])

    # Style
    apply_paper_style(ax, title=title, ylabel='Average Number of EES/MES Executions')
    ax.set_xticks(x)
    ax.set_xticklabels(methods, fontsize=FONT_SIZES['tick_label'])
    ax.legend(loc='upper right', fontsize=FONT_SIZES['legend'])

    # Remove x-axis label
    ax.set_xlabel('')

    plt.tight_layout()
    return fig


def plot_efficiency_comparison_bars(
    data: Dict[str, Dict[str, float]],
    title: str = 'Spending Efficiency Comparison',
    figsize: Tuple[float, float] = None,
    ax: plt.Axes = None
) -> plt.Figure:
    """
    Create a grouped bar chart comparing spending efficiency across methods.

    Args:
        data: Dictionary with method names as keys and
              {'cost': value, 'cardinal': value} as values
        title: Plot title
        figsize: Figure size
        ax: Existing axes to plot on

    Returns:
        Matplotlib Figure object
    """
    if figsize is None:
        figsize = (8, 5)

    if ax is None:
        fig, ax = plt.subplots(figsize=figsize)
    else:
        fig = ax.get_figure()

    methods = list(data.keys())
    n_methods = len(methods)

    # Extract values
    cost_values = [data[m].get('cost', 0) for m in methods]
    cardinal_values = [data[m].get('cardinal', 0) for m in methods]

    # Bar positions
    x = np.arange(n_methods)
    width = 0.35

    # Create bars
    bars1 = ax.bar(x - width/2, cost_values, width,
                   label='Cost', color=PAPER_COLORS['cost'], alpha=0.8)
    bars2 = ax.bar(x + width/2, cardinal_values, width,
                   label='Cardinal', color=PAPER_COLORS['cardinal'], alpha=0.8)

    # Add value labels on bars
    for bar in bars1:
        height = bar.get_height()
        ax.annotate(f'{height:.2f}',
                    xy=(bar.get_x() + bar.get_width() / 2, height),
                    xytext=(0, 3),
                    textcoords="offset points",
                    ha='center', va='bottom',
                    fontsize=FONT_SIZES['annotation'])

    for bar in bars2:
        height = bar.get_height()
        ax.annotate(f'{height:.2f}',
                    xy=(bar.get_x() + bar.get_width() / 2, height),
                    xytext=(0, 3),
                    textcoords="offset points",
                    ha='center', va='bottom',
                    fontsize=FONT_SIZES['annotation'])

    # Style
    apply_paper_style(ax, title=title, ylabel='Average Spending Efficiency')
    ax.set_xticks(x)
    ax.set_xticklabels(methods, fontsize=FONT_SIZES['tick_label'])
    ax.legend(loc='lower right', fontsize=FONT_SIZES['legend'])
    ax.set_ylim(0, 1.2)

    # Remove x-axis label
    ax.set_xlabel('')

    plt.tight_layout()
    return fig


def plot_figure_3(
    data: Dict = None,
    figsize: Tuple[float, float] = None
) -> Tuple[plt.Figure, plt.Figure]:
    """
    Create Figure 3: Executions and efficiency comparison (two panels).

    Args:
        data: Dictionary with 'executions' and 'efficiency' keys
        figsize: Figure size for each subplot

    Returns:
        Tuple of (executions_figure, efficiency_figure)
    """
    if data is None:
        from .sample_data import generate_execution_comparison_data
        data = generate_execution_comparison_data()

    if figsize is None:
        figsize = FIGURE_SIZES['bars_pair']

    # Create combined figure
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=figsize)

    # Left: Executions comparison
    exec_data = data['executions']
    methods = list(exec_data.keys())
    n_methods = len(methods)

    cost_values = [exec_data[m].get('cost', 0) for m in methods]
    cardinal_values = [exec_data[m].get('cardinal', 0) for m in methods]

    x = np.arange(n_methods)
    width = 0.35

    bars1 = ax1.bar(x - width/2, cost_values, width,
                    label='Cost', color=PAPER_COLORS['cost'], alpha=0.8)
    bars2 = ax1.bar(x + width/2, cardinal_values, width,
                    label='Cardinal', color=PAPER_COLORS['cardinal'], alpha=0.8)

    for bar in bars1:
        height = bar.get_height()
        ax1.annotate(f'{int(height)}',
                     xy=(bar.get_x() + bar.get_width() / 2, height),
                     xytext=(0, 3), textcoords="offset points",
                     ha='center', va='bottom', fontsize=8, fontweight='bold')

    for bar in bars2:
        height = bar.get_height()
        ax1.annotate(f'{int(height)}',
                     xy=(bar.get_x() + bar.get_width() / 2, height),
                     xytext=(0, 3), textcoords="offset points",
                     ha='center', va='bottom', fontsize=8, fontweight='bold')

    apply_paper_style(ax1, title='Executions Comparison',
                       ylabel='Average Number of EES/MES Executions')
    ax1.set_xticks(x)
    ax1.set_xticklabels(['ADD-ONE\nMES', 'ADD-OPT\nEES', 'ADD-OPT\nSkip', 'MAX'],
                        fontsize=8)
    ax1.legend(loc='upper right', fontsize=8)

    # Right: Efficiency comparison
    eff_data = data['efficiency']

    cost_values = [eff_data[m].get('cost', 0) for m in methods]
    cardinal_values = [eff_data[m].get('cardinal', 0) for m in methods]

    bars1 = ax2.bar(x - width/2, cost_values, width,
                    label='Cost', color=PAPER_COLORS['cost'], alpha=0.8)
    bars2 = ax2.bar(x + width/2, cardinal_values, width,
                    label='Cardinal', color=PAPER_COLORS['cardinal'], alpha=0.8)

    for bar in bars1:
        height = bar.get_height()
        ax2.annotate(f'{height:.2f}',
                     xy=(bar.get_x() + bar.get_width() / 2, height),
                     xytext=(0, 3), textcoords="offset points",
                     ha='center', va='bottom', fontsize=8)

    for bar in bars2:
        height = bar.get_height()
        ax2.annotate(f'{height:.2f}',
                     xy=(bar.get_x() + bar.get_width() / 2, height),
                     xytext=(0, 3), textcoords="offset points",
                     ha='center', va='bottom', fontsize=8)

    apply_paper_style(ax2, title='Spending Efficiency Comparison',
                       ylabel='Average Spending Efficiency')
    ax2.set_xticks(x)
    ax2.set_xticklabels(['ADD-ONE\nMES', 'ADD-OPT\nEES', 'ADD-OPT\nSkip', 'MAX'],
                        fontsize=8)
    ax2.legend(loc='lower right', fontsize=8)
    ax2.set_ylim(0, 1.1)

    # Label subplots
    ax1.text(-0.12, 1.05, '(a) EES vs. MES number of iterations',
             transform=ax1.transAxes, fontsize=10, fontweight='bold', va='bottom')
    ax2.text(-0.12, 1.05, '(b) EES vs. MES spending efficiency',
             transform=ax2.transAxes, fontsize=10, fontweight='bold', va='bottom')

    plt.tight_layout()
    return fig, None  # Return single combined figure


def plot_figure_4(
    data: Dict = None,
    figsize: Tuple[float, float] = None
) -> plt.Figure:
    """
    Create Figure 4: Non-monotonic instances comparison.

    Args:
        data: Dictionary with execution and efficiency data for non-monotonic instances
        figsize: Figure size

    Returns:
        Matplotlib Figure object
    """
    if data is None:
        from .sample_data import generate_non_monotonic_data
        data = generate_non_monotonic_data()

    if figsize is None:
        figsize = FIGURE_SIZES['bars_pair']

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=figsize)

    methods = list(data['executions'].keys())
    n_methods = len(methods)
    x = np.arange(n_methods)
    width = 0.35

    # Left: Executions
    exec_data = data['executions']
    cost_values = [exec_data[m].get('cost', 0) for m in methods]
    cardinal_values = [exec_data[m].get('cardinal', 0) for m in methods]

    bars1 = ax1.bar(x - width/2, cost_values, width,
                    label='Cost', color=PAPER_COLORS['cost'], alpha=0.8)
    bars2 = ax1.bar(x + width/2, cardinal_values, width,
                    label='Cardinal', color=PAPER_COLORS['cardinal'], alpha=0.8)

    for bar in bars1:
        height = bar.get_height()
        ax1.annotate(f'{int(height)}',
                     xy=(bar.get_x() + bar.get_width() / 2, height),
                     xytext=(0, 3), textcoords="offset points",
                     ha='center', va='bottom', fontsize=9, fontweight='bold')

    for bar in bars2:
        height = bar.get_height()
        ax1.annotate(f'{int(height)}',
                     xy=(bar.get_x() + bar.get_width() / 2, height),
                     xytext=(0, 3), textcoords="offset points",
                     ha='center', va='bottom', fontsize=9, fontweight='bold')

    apply_paper_style(ax1, title='Executions\nfor Selected Instances',
                       ylabel='Number of Executions')
    ax1.set_xticks(x)
    ax1.set_xticklabels(['MES +\nAdd-One', 'EES +\nAdd-Opt-Skip'], fontsize=9)
    ax1.legend(loc='upper right', fontsize=8)

    # Right: Efficiency
    eff_data = data['efficiency']
    cost_values = [eff_data[m].get('cost', 0) for m in methods]
    cardinal_values = [eff_data[m].get('cardinal', 0) for m in methods]

    bars1 = ax2.bar(x - width/2, cost_values, width,
                    label='Cost', color=PAPER_COLORS['cost'], alpha=0.8)
    bars2 = ax2.bar(x + width/2, cardinal_values, width,
                    label='Cardinal', color=PAPER_COLORS['cardinal'], alpha=0.8)

    for bar in bars1:
        height = bar.get_height()
        ax2.annotate(f'{height:.2f}',
                     xy=(bar.get_x() + bar.get_width() / 2, height),
                     xytext=(0, 3), textcoords="offset points",
                     ha='center', va='bottom', fontsize=9)

    for bar in bars2:
        height = bar.get_height()
        ax2.annotate(f'{height:.2f}',
                     xy=(bar.get_x() + bar.get_width() / 2, height),
                     xytext=(0, 3), textcoords="offset points",
                     ha='center', va='bottom', fontsize=9)

    apply_paper_style(ax2, title='Efficiency\nfor Selected Instances',
                       ylabel='Efficiency')
    ax2.set_xticks(x)
    ax2.set_xticklabels(['MES +\nAdd-One', 'EES +\nAdd-Opt-Skip'], fontsize=9)
    ax2.legend(loc='upper right', fontsize=8)
    ax2.set_ylim(0, 1.0)

    plt.tight_layout()
    return fig


def create_all_bar_figures(data: Dict = None) -> Dict[str, plt.Figure]:
    """
    Create all bar chart figures.

    Args:
        data: Optional data dictionary with all required data

    Returns:
        Dictionary mapping figure names to Figure objects
    """
    figures = {}

    # Figure 3
    fig3_data = data.get('figure_3') if data else None
    figures['figure_3'], _ = plot_figure_3(fig3_data)

    # Figure 4
    fig4_data = data.get('figure_4') if data else None
    figures['figure_4'] = plot_figure_4(fig4_data)

    return figures
