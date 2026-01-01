"""
Visualizations package for "Streamlining Equal Shares" paper.

Provides functions to generate all figures from the paper:
- Figures 1, 10: Budget trajectory plots (efficiency vs budget + project selection)
- Figure 2: MES vs EES scatter plots with ADD-ONE
- Figures 3, 4: Execution and efficiency comparison bar charts
- Figures 5, 6: EES ADD-OPT-SKIP vs MES ADD-ONE scatter plots
- Figure 7: Dataset characteristics (histograms and scatter)
- Figures 8, 9: Raw MES vs EES comparison scatter plots
"""

__version__ = '1.0.0'

# Core utilities
from .utils import (
    parse_fraction,
    parse_project_list,
    parse_ordered_dict,
    calculate_efficiency,
    compare_efficiencies,
    calculate_percentages
)

# Data loading
from .data_loader import (
    load_single_result,
    load_results_folder,
    load_all_results,
    aggregate_for_comparison,
    get_efficiency_statistics,
    get_execution_statistics
)

# Sample data generation
from .sample_data import (
    generate_stare_wlochy_data,
    generate_stare_implementation_data,
    generate_comparison_data,
    generate_execution_comparison_data,
    generate_non_monotonic_data,
    generate_dataset_statistics,
    generate_raw_comparison_data,
    generate_add_opt_skip_comparison_data,
    get_all_sample_data
)

# Efficiency scatter plots (Figures 2, 5, 6, 8, 9)
from .efficiency_scatter import (
    plot_efficiency_scatter,
    plot_figure_2,
    plot_figures_5_6,
    plot_figures_8_9,
    create_all_scatter_figures
)

# Comparison bar charts (Figures 3, 4)
from .comparison_bars import (
    plot_executions_comparison,
    plot_efficiency_comparison_bars,
    plot_figure_3,
    plot_figure_4,
    create_all_bar_figures
)

# Budget trajectory plots (Figures 1, 10)
from .budget_trajectory import (
    plot_efficiency_vs_budget,
    plot_project_selection_timeline,
    plot_combined_budget_figure,
    plot_figure_1,
    plot_figure_10,
    create_all_trajectory_figures
)

# Dataset statistics (Figure 7)
from .dataset_stats import (
    plot_voters_vs_budget,
    plot_distribution_histogram,
    plot_figure_7,
    calculate_dataset_statistics,
    create_all_stats_figures
)

# Style configuration
from .style_config import (
    PAPER_COLORS,
    FIGURE_SIZES,
    FONT_SIZES,
    apply_paper_style,
    get_project_colors
)


def create_all_figures(data=None, output_dir=None):
    """
    Generate all paper figures.

    Args:
        data: Optional dictionary with all data for figures
        output_dir: Optional directory to save figures

    Returns:
        Dictionary mapping figure names to Figure objects
    """
    import matplotlib.pyplot as plt
    from pathlib import Path

    if data is None:
        data = get_all_sample_data()

    figures = {}

    # Figure 1
    figures['figure_1'] = plot_figure_1(data.get('figure_1'))

    # Figure 2
    figures['figure_2'] = plot_figure_2(data.get('figure_2'))

    # Figure 3
    fig3, _ = plot_figure_3(data.get('figure_3'))
    figures['figure_3'] = fig3

    # Figure 4
    figures['figure_4'] = plot_figure_4(data.get('figure_4'))

    # Figures 5 and 6
    fig5, fig6 = plot_figures_5_6(data.get('figures_5_6'))
    figures['figure_5'] = fig5
    figures['figure_6'] = fig6

    # Figure 7
    figures['figure_7'] = plot_figure_7(data.get('figure_7'))

    # Figures 8 and 9
    fig8, fig9 = plot_figures_8_9(data.get('figures_8_9'))
    figures['figure_8'] = fig8
    figures['figure_9'] = fig9

    # Figure 10
    figures['figure_10'] = plot_figure_10(data.get('figure_10'))

    # Save if output directory specified
    if output_dir:
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)

        for name, fig in figures.items():
            if fig is not None:
                fig.savefig(output_path / f'{name}.png', dpi=300, bbox_inches='tight')
                fig.savefig(output_path / f'{name}.pdf', bbox_inches='tight')

    return figures


__all__ = [
    # Version
    '__version__',

    # Utils
    'parse_fraction',
    'parse_project_list',
    'parse_ordered_dict',
    'calculate_efficiency',
    'compare_efficiencies',
    'calculate_percentages',

    # Data loading
    'load_single_result',
    'load_results_folder',
    'load_all_results',
    'aggregate_for_comparison',
    'get_efficiency_statistics',
    'get_execution_statistics',

    # Sample data
    'generate_stare_wlochy_data',
    'generate_stare_implementation_data',
    'generate_comparison_data',
    'generate_execution_comparison_data',
    'generate_non_monotonic_data',
    'generate_dataset_statistics',
    'generate_raw_comparison_data',
    'generate_add_opt_skip_comparison_data',
    'get_all_sample_data',

    # Plotting functions
    'plot_efficiency_scatter',
    'plot_figure_1',
    'plot_figure_2',
    'plot_figure_3',
    'plot_figure_4',
    'plot_figures_5_6',
    'plot_figure_7',
    'plot_figures_8_9',
    'plot_figure_10',
    'plot_efficiency_vs_budget',
    'plot_project_selection_timeline',
    'plot_combined_budget_figure',
    'plot_executions_comparison',
    'plot_efficiency_comparison_bars',
    'plot_voters_vs_budget',
    'plot_distribution_histogram',
    'calculate_dataset_statistics',

    # Batch creation
    'create_all_figures',
    'create_all_scatter_figures',
    'create_all_bar_figures',
    'create_all_trajectory_figures',
    'create_all_stats_figures',

    # Style
    'PAPER_COLORS',
    'FIGURE_SIZES',
    'FONT_SIZES',
    'apply_paper_style',
    'get_project_colors',
]
