#!/usr/bin/env python3
"""
Demo script for generating all paper visualizations.

This script:
1. Loads results from Scalable_Proportional_PB/results/
2. Generates sample data for trajectory plots
3. Creates all figures matching the paper
4. Saves figures to output/ folder
5. Prints verification summary

Usage:
    python -m visualizations.demo
    # or
    python visualizations/demo.py
"""

import os
import sys
from pathlib import Path

import matplotlib
matplotlib.use('Agg')  # Use non-interactive backend
import matplotlib.pyplot as plt

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from visualizations import (
    # Data loading
    load_all_results,
    aggregate_for_comparison,
    get_efficiency_statistics,
    get_execution_statistics,

    # Sample data
    get_all_sample_data,

    # Figure plotting
    plot_figure_1,
    plot_figure_2,
    plot_figure_3,
    plot_figure_4,
    plot_figures_5_6,
    plot_figure_7,
    plot_figures_8_9,
    plot_figure_10,

    # Batch creation
    create_all_figures
)


def get_results_path() -> Path:
    """Get path to results folder."""
    # Try relative to this file
    base_path = Path(__file__).parent.parent
    results_path = base_path / 'Scalable_Proportional_PB' / 'results'

    if results_path.exists():
        return results_path

    # Try as submodule
    results_path = base_path / 'results'
    if results_path.exists():
        return results_path

    return None


def print_results_summary(results: dict) -> None:
    """Print summary of loaded results."""
    print("\n" + "=" * 60)
    print("RESULTS SUMMARY")
    print("=" * 60)

    for method, utility_data in results.items():
        print(f"\n{method}:")
        for utility, variant_data in utility_data.items():
            print(f"  {utility}:")
            for variant, df in variant_data.items():
                if not df.empty:
                    count = len(df)
                    stats = get_efficiency_statistics(df)
                    mean_eff = stats.get('mean', 0)
                    print(f"    {variant}: {count} instances (avg efficiency: {mean_eff:.3f})")
                else:
                    print(f"    {variant}: No data")


def generate_all_figures(output_dir: Path, use_real_data: bool = True) -> dict:
    """
    Generate all paper figures.

    Args:
        output_dir: Directory to save figures
        use_real_data: Whether to try loading real results

    Returns:
        Dictionary of generated figures
    """
    output_dir.mkdir(parents=True, exist_ok=True)

    print("\n" + "=" * 60)
    print("GENERATING FIGURES")
    print("=" * 60)

    # Get sample data for all figures
    sample_data = get_all_sample_data()

    figures = {}

    # Figure 1: Efficiency vs Budget (Stare, Włochy)
    print("\nGenerating Figure 1: Budget Trajectory (Stare, Włochy)...")
    try:
        fig1 = plot_figure_1(sample_data['figure_1'])
        fig1.savefig(output_dir / 'figure_1.png', dpi=300, bbox_inches='tight')
        fig1.savefig(output_dir / 'figure_1.pdf', bbox_inches='tight')
        figures['figure_1'] = fig1
        print("  ✓ Figure 1 saved")
    except Exception as e:
        print(f"  ✗ Figure 1 failed: {e}")

    # Figure 2: MES vs EES scatter plots
    print("\nGenerating Figure 2: MES vs EES Comparison...")
    try:
        fig2 = plot_figure_2(sample_data['figure_2'])
        fig2.savefig(output_dir / 'figure_2.png', dpi=300, bbox_inches='tight')
        fig2.savefig(output_dir / 'figure_2.pdf', bbox_inches='tight')
        figures['figure_2'] = fig2
        print("  ✓ Figure 2 saved")
    except Exception as e:
        print(f"  ✗ Figure 2 failed: {e}")

    # Figure 3: Executions and Efficiency Comparison
    print("\nGenerating Figure 3: Executions & Efficiency Comparison...")
    try:
        fig3, _ = plot_figure_3(sample_data['figure_3'])
        fig3.savefig(output_dir / 'figure_3.png', dpi=300, bbox_inches='tight')
        fig3.savefig(output_dir / 'figure_3.pdf', bbox_inches='tight')
        figures['figure_3'] = fig3
        print("  ✓ Figure 3 saved")
    except Exception as e:
        print(f"  ✗ Figure 3 failed: {e}")

    # Figure 4: Non-monotonic instances
    print("\nGenerating Figure 4: Non-Monotonic Instances...")
    try:
        fig4 = plot_figure_4(sample_data['figure_4'])
        fig4.savefig(output_dir / 'figure_4.png', dpi=300, bbox_inches='tight')
        fig4.savefig(output_dir / 'figure_4.pdf', bbox_inches='tight')
        figures['figure_4'] = fig4
        print("  ✓ Figure 4 saved")
    except Exception as e:
        print(f"  ✗ Figure 4 failed: {e}")

    # Figures 5 & 6: ADD-OPT-SKIP comparison
    print("\nGenerating Figures 5 & 6: ADD-OPT-SKIP vs ADD-ONE...")
    try:
        fig5, fig6 = plot_figures_5_6(sample_data['figures_5_6'])
        fig5.savefig(output_dir / 'figure_5.png', dpi=300, bbox_inches='tight')
        fig5.savefig(output_dir / 'figure_5.pdf', bbox_inches='tight')
        fig6.savefig(output_dir / 'figure_6.png', dpi=300, bbox_inches='tight')
        fig6.savefig(output_dir / 'figure_6.pdf', bbox_inches='tight')
        figures['figure_5'] = fig5
        figures['figure_6'] = fig6
        print("  ✓ Figures 5 & 6 saved")
    except Exception as e:
        print(f"  ✗ Figures 5 & 6 failed: {e}")

    # Figure 7: Dataset characteristics
    print("\nGenerating Figure 7: Dataset Statistics...")
    try:
        fig7 = plot_figure_7(sample_data['figure_7'])
        fig7.savefig(output_dir / 'figure_7.png', dpi=300, bbox_inches='tight')
        fig7.savefig(output_dir / 'figure_7.pdf', bbox_inches='tight')
        figures['figure_7'] = fig7
        print("  ✓ Figure 7 saved")
    except Exception as e:
        print(f"  ✗ Figure 7 failed: {e}")

    # Figures 8 & 9: Raw MES vs EES
    print("\nGenerating Figures 8 & 9: Raw MES vs EES...")
    try:
        fig8, fig9 = plot_figures_8_9(sample_data['figures_8_9'])
        fig8.savefig(output_dir / 'figure_8.png', dpi=300, bbox_inches='tight')
        fig8.savefig(output_dir / 'figure_8.pdf', bbox_inches='tight')
        fig9.savefig(output_dir / 'figure_9.png', dpi=300, bbox_inches='tight')
        fig9.savefig(output_dir / 'figure_9.pdf', bbox_inches='tight')
        figures['figure_8'] = fig8
        figures['figure_9'] = fig9
        print("  ✓ Figures 8 & 9 saved")
    except Exception as e:
        print(f"  ✗ Figures 8 & 9 failed: {e}")

    # Figure 10: Stare implementation
    print("\nGenerating Figure 10: Stare Implementation...")
    try:
        fig10 = plot_figure_10(sample_data['figure_10'])
        fig10.savefig(output_dir / 'figure_10.png', dpi=300, bbox_inches='tight')
        fig10.savefig(output_dir / 'figure_10.pdf', bbox_inches='tight')
        figures['figure_10'] = fig10
        print("  ✓ Figure 10 saved")
    except Exception as e:
        print(f"  ✗ Figure 10 failed: {e}")

    return figures


def verify_figures(figures: dict) -> None:
    """Print verification summary of generated figures."""
    print("\n" + "=" * 60)
    print("VERIFICATION SUMMARY")
    print("=" * 60)

    expected_figures = [
        ('figure_1', 'Budget Trajectory - Stare, Włochy'),
        ('figure_2', 'MES vs EES Scatter Plots'),
        ('figure_3', 'Executions & Efficiency Bars'),
        ('figure_4', 'Non-Monotonic Instances'),
        ('figure_5', 'ADD-OPT-SKIP Cardinal'),
        ('figure_6', 'ADD-OPT-SKIP Cost'),
        ('figure_7', 'Dataset Statistics'),
        ('figure_8', 'Raw MES vs EES Cardinal'),
        ('figure_9', 'Raw MES vs EES Cost'),
        ('figure_10', 'Stare Implementation'),
    ]

    generated = 0
    for fig_name, description in expected_figures:
        status = "✓" if fig_name in figures and figures[fig_name] is not None else "✗"
        if status == "✓":
            generated += 1
        print(f"  {status} {fig_name}: {description}")

    print(f"\nTotal: {generated}/{len(expected_figures)} figures generated successfully")


def main():
    """Main entry point for demo."""
    print("=" * 60)
    print("STREAMLINING EQUAL SHARES - VISUALIZATION DEMO")
    print("=" * 60)

    # Determine output directory
    base_path = Path(__file__).parent.parent
    output_dir = base_path / 'output' / 'figures'

    print(f"\nOutput directory: {output_dir}")

    # Try to load real results
    results_path = get_results_path()
    if results_path:
        print(f"Results path found: {results_path}")
        try:
            results = load_all_results(str(results_path))
            print_results_summary(results)
        except Exception as e:
            print(f"Could not load results: {e}")
            results = None
    else:
        print("No results directory found, using sample data only")
        results = None

    # Generate all figures
    figures = generate_all_figures(output_dir)

    # Verify
    verify_figures(figures)

    # Close all figures to free memory
    plt.close('all')

    print("\n" + "=" * 60)
    print("DEMO COMPLETE")
    print("=" * 60)
    print(f"\nFigures saved to: {output_dir}")
    print("Both PNG (300dpi) and PDF formats generated.")


if __name__ == '__main__':
    main()
