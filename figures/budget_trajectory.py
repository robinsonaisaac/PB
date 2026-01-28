"""
Budget trajectory visualizations.
Implements Figures 1 and 10 from the paper.
Shows efficiency vs budget and project selection changes.
"""

import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np
from typing import Dict, List, Tuple, Optional

from .style_config import (
    PAPER_COLORS, FIGURE_SIZES, FONT_SIZES,
    apply_paper_style, get_project_colors, setup_log_scale,
    format_budget_axis, add_100_percent_line
)


def plot_efficiency_vs_budget(
    budgets: List[float],
    efficiencies: List[float],
    title: str = 'Spending Efficiency vs. Budget',
    log_scale: bool = True,
    show_100_percent_line: bool = True,
    figsize: Tuple[float, float] = None,
    ax: plt.Axes = None
) -> plt.Axes:
    """
    Create a line plot of spending efficiency vs budget.

    Args:
        budgets: Budget values (x-axis)
        efficiencies: Efficiency values (y-axis)
        title: Plot title
        log_scale: Whether to use log scale for x-axis
        show_100_percent_line: Whether to show 100% efficiency reference
        figsize: Figure size
        ax: Existing axes to plot on

    Returns:
        Matplotlib Axes object
    """
    if ax is None:
        if figsize is None:
            figsize = (6, 5)
        fig, ax = plt.subplots(figsize=figsize)

    # Convert to numpy arrays
    x = np.array(budgets)
    y = np.array(efficiencies)

    # Plot efficiency line with step-like appearance
    ax.plot(x, y, color=PAPER_COLORS['ees'], linewidth=2,
            marker='o', markersize=4, drawstyle='steps-post')

    # Apply styling
    apply_paper_style(ax, title=title)

    # Set scales and labels
    if log_scale:
        setup_log_scale(ax, axis='x')
        format_budget_axis(ax, axis='x')
    else:
        ax.set_xlabel('Budget (PLN)', fontsize=FONT_SIZES['axis_label'])

    ax.set_ylabel('Spending Efficiency', fontsize=FONT_SIZES['axis_label'])

    # Add 100% efficiency reference line
    if show_100_percent_line:
        add_100_percent_line(ax, value=1.0, label='100% SE')

    # Set y-axis limits
    ax.set_ylim(0, 1.1)

    return ax


def plot_project_selection_timeline(
    budgets: List[float],
    project_selections: List[List[str]],
    project_names: List[str],
    project_labels: Dict[str, str] = None,
    log_scale: bool = True,
    figsize: Tuple[float, float] = None,
    ax: plt.Axes = None
) -> plt.Axes:
    """
    Create a horizontal bar chart showing project selection across budgets.

    Args:
        budgets: Budget values
        project_selections: List of selected project sets at each budget
        project_names: All possible project names/IDs
        project_labels: Optional mapping from IDs to display names
        log_scale: Whether to use log scale for x-axis
        figsize: Figure size
        ax: Existing axes to plot on

    Returns:
        Matplotlib Axes object
    """
    if ax is None:
        if figsize is None:
            figsize = (6, 5)
        fig, ax = plt.subplots(figsize=figsize)

    # Use display labels if provided
    if project_labels is None:
        project_labels = {p: p for p in project_names}

    # Get colors for projects
    colors = get_project_colors(project_names)

    # Create project index mapping (reversed for top-to-bottom display)
    n_projects = len(project_names)
    project_indices = {p: n_projects - i - 1 for i, p in enumerate(project_names)}

    # Track budget ranges for each project
    project_ranges = {p: [] for p in project_names}

    for i in range(len(budgets)):
        current_budget = budgets[i]
        next_budget = budgets[i + 1] if i + 1 < len(budgets) else current_budget * 1.1
        current_projects = set(project_selections[i])

        for project in project_names:
            if project in current_projects:
                project_ranges[project].append((current_budget, next_budget))

    # Merge consecutive ranges
    for project in project_names:
        ranges = project_ranges[project]
        if not ranges:
            continue

        merged = []
        current_start, current_end = ranges[0]

        for start, end in ranges[1:]:
            if start <= current_end:
                current_end = max(current_end, end)
            else:
                merged.append((current_start, current_end))
                current_start, current_end = start, end

        merged.append((current_start, current_end))
        project_ranges[project] = merged

    # Plot horizontal bars
    bar_height = 0.7
    for project in project_names:
        y_pos = project_indices[project]
        for start, end in project_ranges[project]:
            width = end - start
            ax.barh(y_pos, width, left=start, height=bar_height,
                    color=colors[project], alpha=0.8, edgecolor='white')

    # Set y-axis ticks and labels
    ax.set_yticks(range(n_projects))
    display_labels = [project_labels.get(p, p) for p in reversed(project_names)]
    ax.set_yticklabels(display_labels, fontsize=FONT_SIZES['tick_label'])

    # Apply styling
    apply_paper_style(ax, title='Project Selection vs. Budget')

    # Set scales
    if log_scale:
        setup_log_scale(ax, axis='x')
        format_budget_axis(ax, axis='x')
    else:
        ax.set_xlabel('Budget (PLN)', fontsize=FONT_SIZES['axis_label'])

    # Remove y-axis label
    ax.set_ylabel('')

    # Set x limits to match efficiency plot
    ax.set_xlim(min(budgets) * 0.95, max(budgets) * 1.05)

    return ax


def plot_combined_budget_figure(
    budgets: List[float],
    efficiencies: List[float],
    project_selections: List[List[str]],
    project_names: List[str],
    title: str = 'Efficiency and Project Selection vs. Budget',
    project_labels: Dict[str, str] = None,
    log_scale: bool = True,
    figsize: Tuple[float, float] = None
) -> plt.Figure:
    """
    Create a two-panel figure with efficiency and project selection.

    Args:
        budgets: Budget values
        efficiencies: Efficiency values
        project_selections: Project selections at each budget
        project_names: All project names
        title: Overall figure title
        project_labels: Optional mapping to display names
        log_scale: Whether to use log scale
        figsize: Figure size

    Returns:
        Matplotlib Figure object
    """
    if figsize is None:
        figsize = FIGURE_SIZES['trajectory']

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=figsize)

    # Left: Efficiency vs Budget
    plot_efficiency_vs_budget(
        budgets, efficiencies,
        title='Spending Efficiency',
        log_scale=log_scale,
        ax=ax1
    )

    # Right: Project Selection Timeline
    plot_project_selection_timeline(
        budgets, project_selections, project_names,
        project_labels=project_labels,
        log_scale=log_scale,
        ax=ax2
    )

    # Synchronize x-axis limits
    xlim = (min(budgets) * 0.95, max(budgets) * 1.05)
    ax1.set_xlim(xlim)
    ax2.set_xlim(xlim)

    # Add overall title
    fig.suptitle(title, fontsize=FONT_SIZES['title'] + 2, fontweight='bold', y=1.02)

    plt.tight_layout()
    return fig


def plot_figure_1(data: Dict = None, figsize: Tuple[float, float] = None) -> plt.Figure:
    """
    Create Figure 1: Stare, Włochy example from the paper.

    Args:
        data: Optional dictionary with budget/efficiency/project data
        figsize: Figure size

    Returns:
        Matplotlib Figure object
    """
    if data is None:
        from .sample_data import generate_stare_wlochy_data
        data = generate_stare_wlochy_data()

    if figsize is None:
        figsize = FIGURE_SIZES['trajectory']

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=figsize)

    budgets = data['budgets']
    efficiencies = data['efficiencies']
    project_selections = data['project_selections']
    project_names = data['project_names']
    location = data.get('location', 'Stare, Włochy')

    # Left panel: Efficiency vs Budget
    x = np.array(budgets)
    y = np.array(efficiencies)

    # Create step plot for efficiency
    ax1.step(x, y, where='post', color=PAPER_COLORS['ees'], linewidth=2)
    ax1.scatter(x, y, color=PAPER_COLORS['ees'], s=30, zorder=5)

    # Add 100% reference line
    ax1.axhline(y=1.0, color=PAPER_COLORS['reference_line'],
                linestyle='--', alpha=0.7, label='100% SE')

    apply_paper_style(ax1, title=f'Efficiency vs. Budget for {location}',
                       ylabel='Spending Efficiency')
    setup_log_scale(ax1, axis='x')
    format_budget_axis(ax1, axis='x')
    ax1.set_ylim(0, 1.1)
    ax1.legend(loc='lower right', fontsize=FONT_SIZES['legend'])

    # Right panel: Project Selection
    colors = get_project_colors(project_names)
    n_projects = len(project_names)
    project_indices = {p: n_projects - i - 1 for i, p in enumerate(project_names)}

    # Calculate selection ranges
    bar_height = 0.7

    for i in range(len(budgets)):
        current_budget = budgets[i]
        next_budget = budgets[i + 1] if i + 1 < len(budgets) else current_budget * 1.1
        current_projects = set(project_selections[i])

        for project in project_names:
            if project in current_projects:
                y_pos = project_indices[project]
                width = next_budget - current_budget
                ax2.barh(y_pos, width, left=current_budget, height=bar_height,
                        color=colors[project], alpha=0.8, edgecolor='white', linewidth=0.5)

    # Configure right panel
    ax2.set_yticks(range(n_projects))
    ax2.set_yticklabels(list(reversed(project_names)), fontsize=FONT_SIZES['tick_label'])

    apply_paper_style(ax2, title='Project Selection')
    setup_log_scale(ax2, axis='x')
    format_budget_axis(ax2, axis='x')
    ax2.set_ylabel('')

    # Synchronize x-axis
    xlim = (min(budgets) * 0.95, max(budgets) * 1.05)
    ax1.set_xlim(xlim)
    ax2.set_xlim(xlim)

    # Add subplot labels
    ax1.text(-0.12, 1.05, '(a)', transform=ax1.transAxes,
             fontsize=12, fontweight='bold', va='bottom')
    ax2.text(-0.12, 1.05, '(b)', transform=ax2.transAxes,
             fontsize=12, fontweight='bold', va='bottom')

    plt.tight_layout()
    return fig


def plot_figure_10(data: Dict = None, figsize: Tuple[float, float] = None) -> plt.Figure:
    """
    Create Figure 10: Stare implementation case study.

    Args:
        data: Optional dictionary with budget/efficiency/project data
        figsize: Figure size

    Returns:
        Matplotlib Figure object
    """
    if data is None:
        from .sample_data import generate_stare_implementation_data
        data = generate_stare_implementation_data()

    if figsize is None:
        figsize = (14, 6)  # Wider for more projects

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=figsize)

    budgets = data['budgets']
    efficiencies = data['efficiencies']
    project_selections = data['project_selections']
    project_names = data['project_names']
    location = data.get('location', 'Stare, Poland')

    # Left panel: Efficiency vs Budget
    x = np.array(budgets)
    y = np.array(efficiencies)

    ax1.plot(x, y, color=PAPER_COLORS['ees'], linewidth=2, marker='o', markersize=3)

    # Add reference line
    ax1.axhline(y=1.0, color=PAPER_COLORS['reference_line'],
                linestyle='--', alpha=0.7, label='100% SE')

    apply_paper_style(ax1, title=f'Efficiency vs. Budget for {location}',
                       ylabel='Spending Efficiency')
    setup_log_scale(ax1, axis='x')
    format_budget_axis(ax1, axis='x')
    ax1.set_ylim(0, 1.1)
    ax1.legend(loc='lower right', fontsize=FONT_SIZES['legend'])

    # Right panel: Project Selection
    colors = get_project_colors(project_names)
    n_projects = len(project_names)
    project_indices = {p: n_projects - i - 1 for i, p in enumerate(project_names)}

    bar_height = 0.6

    for i in range(len(budgets)):
        current_budget = budgets[i]
        next_budget = budgets[i + 1] if i + 1 < len(budgets) else current_budget * 1.05
        current_projects = set(project_selections[i])

        for project in project_names:
            if project in current_projects:
                y_pos = project_indices[project]
                width = next_budget - current_budget
                ax2.barh(y_pos, width, left=current_budget, height=bar_height,
                        color=colors[project], alpha=0.8, edgecolor='white', linewidth=0.3)

    # Configure right panel
    ax2.set_yticks(range(n_projects))
    # Truncate long names for display
    display_names = [p[:15] + '...' if len(p) > 15 else p for p in reversed(project_names)]
    ax2.set_yticklabels(display_names, fontsize=FONT_SIZES['tick_label'] - 1)

    apply_paper_style(ax2, title='Project Selection Over Budget')
    setup_log_scale(ax2, axis='x')
    format_budget_axis(ax2, axis='x')
    ax2.set_ylabel('')

    # Synchronize x-axis
    xlim = (min(budgets) * 0.95, max(budgets) * 1.05)
    ax1.set_xlim(xlim)
    ax2.set_xlim(xlim)

    # Add subplot labels
    ax1.text(-0.12, 1.05, '(a)', transform=ax1.transAxes,
             fontsize=12, fontweight='bold', va='bottom')
    ax2.text(-0.12, 1.05, '(b)', transform=ax2.transAxes,
             fontsize=12, fontweight='bold', va='bottom')

    plt.tight_layout()
    return fig


def create_all_trajectory_figures(data: Dict = None) -> Dict[str, plt.Figure]:
    """
    Create all trajectory figures.

    Args:
        data: Optional data dictionary

    Returns:
        Dictionary mapping figure names to Figure objects
    """
    figures = {}

    # Figure 1
    fig1_data = data.get('figure_1') if data else None
    figures['figure_1'] = plot_figure_1(fig1_data)

    # Figure 10
    fig10_data = data.get('figure_10') if data else None
    figures['figure_10'] = plot_figure_10(fig10_data)

    return figures
