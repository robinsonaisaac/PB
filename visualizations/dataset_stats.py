"""
Dataset statistics visualizations.
Implements Figure 7 from the paper.
Shows distribution of voters, projects, and budgets.
"""

import matplotlib.pyplot as plt
import numpy as np
from typing import Dict, List, Tuple, Optional

# scipy is optional - use numpy fallback if not available
try:
    from scipy import stats as scipy_stats
    HAS_SCIPY = True
except ImportError:
    HAS_SCIPY = False

from .style_config import (
    PAPER_COLORS, FIGURE_SIZES, FONT_SIZES,
    apply_paper_style, setup_log_scale, add_correlation_annotation,
    add_percentile_lines
)


def _pearsonr(x: np.ndarray, y: np.ndarray) -> float:
    """
    Calculate Pearson correlation coefficient.
    Uses scipy if available, otherwise numpy fallback.
    """
    if HAS_SCIPY:
        return scipy_stats.pearsonr(x, y)[0]
    else:
        # Numpy fallback
        return np.corrcoef(x, y)[0, 1]


def plot_voters_vs_budget(
    voters: List[int],
    budgets: List[float],
    title: str = 'Number of Voters vs. Budget',
    show_correlation: bool = True,
    figsize: Tuple[float, float] = None,
    ax: plt.Axes = None
) -> plt.Axes:
    """
    Create a scatter plot of voters vs budget.

    Args:
        voters: Number of voters per instance
        budgets: Budget values per instance
        title: Plot title
        show_correlation: Whether to show correlation coefficient
        figsize: Figure size
        ax: Existing axes to plot on

    Returns:
        Matplotlib Axes object
    """
    if ax is None:
        if figsize is None:
            figsize = (6, 5)
        fig, ax = plt.subplots(figsize=figsize)

    # Convert to arrays
    x = np.array(voters)
    y = np.array(budgets)

    # Create scatter plot
    ax.scatter(x, y, c=PAPER_COLORS['mes'], s=20, alpha=0.6, edgecolors='white', linewidths=0.3)

    # Apply styling
    apply_paper_style(ax, title=title,
                       xlabel='Number of Voters',
                       ylabel='Budget')

    # Set log scales
    setup_log_scale(ax, axis='both')

    # Calculate and display correlation
    if show_correlation:
        # Use log values for correlation on log-log plot
        log_x = np.log10(x[x > 0])
        log_y = np.log10(y[y > 0])
        corr = _pearsonr(log_x, log_y)
        add_correlation_annotation(ax, corr)

    return ax


def plot_distribution_histogram(
    data: List[float],
    title: str = 'Distribution',
    xlabel: str = 'Value',
    bins: int = 30,
    log_scale: bool = False,
    percentiles: Dict[int, float] = None,
    show_percentile_lines: bool = True,
    figsize: Tuple[float, float] = None,
    ax: plt.Axes = None
) -> plt.Axes:
    """
    Create a histogram of data distribution.

    Args:
        data: Data values
        title: Plot title
        xlabel: X-axis label
        bins: Number of bins
        log_scale: Whether to use log scale for x-axis
        percentiles: Optional percentile values to display
        show_percentile_lines: Whether to show percentile reference lines
        figsize: Figure size
        ax: Existing axes to plot on

    Returns:
        Matplotlib Axes object
    """
    if ax is None:
        if figsize is None:
            figsize = FIGURE_SIZES['single_histogram']
        fig, ax = plt.subplots(figsize=figsize)

    # Convert to array
    values = np.array(data)

    # Create histogram
    if log_scale:
        # Use log-spaced bins
        log_min = np.log10(max(values.min(), 1))
        log_max = np.log10(values.max())
        bin_edges = np.logspace(log_min, log_max, bins + 1)
        ax.hist(values, bins=bin_edges, color=PAPER_COLORS['mes'],
                alpha=0.7, edgecolor='white', linewidth=0.5)
        setup_log_scale(ax, axis='x')
    else:
        ax.hist(values, bins=bins, color=PAPER_COLORS['mes'],
                alpha=0.7, edgecolor='white', linewidth=0.5)

    # Apply styling
    apply_paper_style(ax, title=title, xlabel=xlabel, ylabel='Count')

    # Add percentile lines
    if show_percentile_lines and percentiles:
        add_percentile_lines(ax, percentiles, orientation='vertical')
        ax.legend(loc='upper right', fontsize=FONT_SIZES['legend'] - 1)

    return ax


def plot_voters_histogram(
    voters: List[int],
    percentiles: Dict[int, float] = None,
    figsize: Tuple[float, float] = None,
    ax: plt.Axes = None
) -> plt.Axes:
    """
    Create histogram of voter distribution.

    Args:
        voters: Number of voters per instance
        percentiles: Optional percentile values
        figsize: Figure size
        ax: Existing axes

    Returns:
        Matplotlib Axes object
    """
    return plot_distribution_histogram(
        voters,
        title='Distribution of Voters',
        xlabel='Number of Voters',
        bins=25,
        log_scale=True,
        percentiles=percentiles,
        figsize=figsize,
        ax=ax
    )


def plot_projects_histogram(
    projects: List[int],
    percentiles: Dict[int, float] = None,
    figsize: Tuple[float, float] = None,
    ax: plt.Axes = None
) -> plt.Axes:
    """
    Create histogram of project count distribution.

    Args:
        projects: Number of projects per instance
        percentiles: Optional percentile values
        figsize: Figure size
        ax: Existing axes

    Returns:
        Matplotlib Axes object
    """
    return plot_distribution_histogram(
        projects,
        title='Distribution of Projects',
        xlabel='Number of Projects',
        bins=25,
        log_scale=False,
        percentiles=percentiles,
        figsize=figsize,
        ax=ax
    )


def plot_budget_histogram(
    budgets: List[float],
    percentiles: Dict[int, float] = None,
    figsize: Tuple[float, float] = None,
    ax: plt.Axes = None
) -> plt.Axes:
    """
    Create histogram of budget distribution.

    Args:
        budgets: Budget values per instance
        percentiles: Optional percentile values
        figsize: Figure size
        ax: Existing axes

    Returns:
        Matplotlib Axes object
    """
    return plot_distribution_histogram(
        budgets,
        title='Distribution of Budgets',
        xlabel='Budget (PLN)',
        bins=25,
        log_scale=True,
        percentiles=percentiles,
        figsize=figsize,
        ax=ax
    )


def plot_figure_7(
    data: Dict = None,
    figsize: Tuple[float, float] = None
) -> plt.Figure:
    """
    Create Figure 7: Dataset characteristics (2x2 grid).

    Args:
        data: Dictionary with 'voters', 'projects', 'budgets' arrays
              and optional 'percentiles' dict
        figsize: Figure size

    Returns:
        Matplotlib Figure object
    """
    if data is None:
        from .sample_data import generate_dataset_statistics
        data = generate_dataset_statistics()

    if figsize is None:
        figsize = FIGURE_SIZES['histogram_quad']

    fig, axes = plt.subplots(2, 2, figsize=figsize)

    voters = data['voters']
    projects = data['projects']
    budgets = data['budgets']
    percentiles = data.get('percentiles', {})

    # (a) Voters vs Budget scatter
    ax_scatter = axes[0, 0]
    x = np.array(voters)
    y = np.array(budgets)

    ax_scatter.scatter(x, y, c=PAPER_COLORS['mes'], s=15, alpha=0.5,
                        edgecolors='white', linewidths=0.2)
    apply_paper_style(ax_scatter, title='(a) Number of Voters vs. Budget',
                       xlabel='Number of Voters', ylabel='Budget')
    setup_log_scale(ax_scatter, axis='both')

    # Calculate correlation
    log_x = np.log10(x[x > 0])
    log_y = np.log10(y[y > 0])
    corr = _pearsonr(log_x, log_y)
    add_correlation_annotation(ax_scatter, corr)

    # (b) Voters histogram
    ax_voters = axes[0, 1]
    voter_data = np.array(voters)
    log_min = np.log10(max(voter_data.min(), 1))
    log_max = np.log10(voter_data.max())
    voter_bins = np.logspace(log_min, log_max, 26)

    ax_voters.hist(voter_data, bins=voter_bins, color=PAPER_COLORS['mes'],
                    alpha=0.7, edgecolor='white', linewidth=0.5)
    apply_paper_style(ax_voters, title='(b) Distribution of Voters',
                       xlabel='Number of Voters', ylabel='Count')
    setup_log_scale(ax_voters, axis='x')

    if 'voters' in percentiles:
        add_percentile_lines(ax_voters, percentiles['voters'])
        ax_voters.legend(loc='upper right', fontsize=7)

    # (c) Projects histogram
    ax_projects = axes[1, 0]
    ax_projects.hist(projects, bins=25, color=PAPER_COLORS['mes'],
                      alpha=0.7, edgecolor='white', linewidth=0.5)
    apply_paper_style(ax_projects, title='(c) Distribution of Projects',
                       xlabel='Number of Projects', ylabel='Count')

    if 'projects' in percentiles:
        add_percentile_lines(ax_projects, percentiles['projects'])
        ax_projects.legend(loc='upper right', fontsize=7)

    # (d) Budget histogram
    ax_budgets = axes[1, 1]
    budget_data = np.array(budgets)
    log_min = np.log10(max(budget_data.min(), 1))
    log_max = np.log10(budget_data.max())
    budget_bins = np.logspace(log_min, log_max, 26)

    ax_budgets.hist(budget_data, bins=budget_bins, color=PAPER_COLORS['mes'],
                     alpha=0.7, edgecolor='white', linewidth=0.5)
    apply_paper_style(ax_budgets, title='(d) Distribution of Budgets',
                       xlabel='Budget', ylabel='Count')
    setup_log_scale(ax_budgets, axis='x')

    if 'budgets' in percentiles:
        add_percentile_lines(ax_budgets, percentiles['budgets'])
        ax_budgets.legend(loc='upper right', fontsize=7)

    plt.tight_layout()
    return fig


def calculate_dataset_statistics(
    voters: List[int],
    projects: List[int],
    budgets: List[float]
) -> Dict:
    """
    Calculate summary statistics for dataset.

    Args:
        voters: Number of voters per instance
        projects: Number of projects per instance
        budgets: Budget values per instance

    Returns:
        Dictionary with statistics
    """
    def get_stats(arr):
        arr = np.array(arr)
        return {
            'min': arr.min(),
            'max': arr.max(),
            'mean': arr.mean(),
            'median': np.median(arr),
            'std': arr.std(),
            'percentile_25': np.percentile(arr, 25),
            'percentile_50': np.percentile(arr, 50),
            'percentile_75': np.percentile(arr, 75),
            'percentile_90': np.percentile(arr, 90),
        }

    return {
        'voters': get_stats(voters),
        'projects': get_stats(projects),
        'budgets': get_stats(budgets),
        'correlation_voters_budget': _pearsonr(
            np.log10(np.array(voters)),
            np.log10(np.array(budgets))
        )
    }


def create_all_stats_figures(data: Dict = None) -> Dict[str, plt.Figure]:
    """
    Create all dataset statistics figures.

    Args:
        data: Optional data dictionary

    Returns:
        Dictionary mapping figure names to Figure objects
    """
    figures = {}

    fig7_data = data.get('figure_7') if data else None
    figures['figure_7'] = plot_figure_7(fig7_data)

    return figures
