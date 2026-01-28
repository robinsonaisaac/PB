"""
Sample and demo data generation for paper visualizations.
Creates data matching the figures in the paper for demonstration.
"""

import numpy as np
from typing import Dict, List


def generate_stare_wlochy_data() -> Dict:
    """
    Generate sample data matching Figure 1 from the paper.
    Stare Włochy district example showing efficiency vs budget.

    Returns:
        Dictionary with budgets, efficiencies, project_selections, and project_names
    """
    # Project names from Figure 1
    project_names = [
        'OCR Training in Mileszki',
        'Nordic Walking in Mileszki',
        'Asphalt on Solecka St.',
        'Gravel on Bratkowa St.'
    ]

    # Budget values (PLN, log scale in figure)
    # The figure shows budget on x-axis from ~3x10^5 to ~6x10^5
    budgets = [
        300000, 320000, 340000, 360000, 380000, 400000,
        420000, 440000, 460000, 480000, 500000, 520000,
        540000, 560000, 580000, 600000, 620000, 640000
    ]

    # Efficiency values matching the stepped pattern in Figure 1
    # Initially low (~0.12), jumps to ~0.6 when Gravel is added,
    # drops when Asphalt is selected, then increases again
    efficiencies = [
        0.12, 0.12, 0.60, 0.60, 0.60, 0.60,
        0.60, 0.60, 0.12, 0.12, 0.12, 0.60,
        0.60, 0.60, 0.60, 0.60, 0.60, 0.60
    ]

    # Project selections at each budget point
    project_selections = [
        ['Nordic Walking in Mileszki'],
        ['Nordic Walking in Mileszki'],
        ['Nordic Walking in Mileszki', 'Gravel on Bratkowa St.'],
        ['Nordic Walking in Mileszki', 'Gravel on Bratkowa St.'],
        ['Nordic Walking in Mileszki', 'Gravel on Bratkowa St.'],
        ['Nordic Walking in Mileszki', 'Gravel on Bratkowa St.'],
        ['Nordic Walking in Mileszki', 'Gravel on Bratkowa St.'],
        ['Nordic Walking in Mileszki', 'Gravel on Bratkowa St.'],
        ['Nordic Walking in Mileszki', 'Asphalt on Solecka St.'],
        ['Nordic Walking in Mileszki', 'Asphalt on Solecka St.'],
        ['Nordic Walking in Mileszki', 'Asphalt on Solecka St.'],
        ['Nordic Walking in Mileszki', 'Gravel on Bratkowa St.', 'OCR Training in Mileszki'],
        ['Nordic Walking in Mileszki', 'Gravel on Bratkowa St.', 'OCR Training in Mileszki'],
        ['Nordic Walking in Mileszki', 'Gravel on Bratkowa St.', 'OCR Training in Mileszki'],
        ['Nordic Walking in Mileszki', 'Gravel on Bratkowa St.', 'OCR Training in Mileszki'],
        ['Nordic Walking in Mileszki', 'Gravel on Bratkowa St.', 'OCR Training in Mileszki'],
        ['Nordic Walking in Mileszki', 'Gravel on Bratkowa St.', 'OCR Training in Mileszki'],
        ['Nordic Walking in Mileszki', 'Gravel on Bratkowa St.', 'OCR Training in Mileszki'],
    ]

    return {
        'budgets': budgets,
        'efficiencies': efficiencies,
        'project_selections': project_selections,
        'project_names': project_names,
        'title': 'Efficiency vs. Budget for Stare, Włochy',
        'location': 'Stare, Włochy'
    }


def generate_stare_implementation_data() -> Dict:
    """
    Generate sample data matching Figure 10 from the paper.
    Stare implementation case study.

    Returns:
        Dictionary with budgets, efficiencies, project_selections, and project_names
    """
    project_names = [
        'Xingg Lights (Ryż.)',
        'Xing Lights (Pop.)',
        'Historical Plaques',
        'Memory Game',
        'Bird Feeding Guide',
        'Bird Houses',
        'Parent Education',
        'Outdoor Chess',
        'Tree Protection',
        'Sports Field',
        'Cycling Infra.',
        'Playgrounds'
    ]

    # Generate budget range from ~3x10^5 to ~8x10^5
    budgets = list(range(300000, 850000, 25000))

    # Generate stepped efficiency pattern
    n = len(budgets)
    efficiencies = []
    for i, b in enumerate(budgets):
        if b < 400000:
            efficiencies.append(0.3 + 0.1 * (b - 300000) / 100000)
        elif b < 500000:
            efficiencies.append(0.6 + 0.1 * (b - 400000) / 100000)
        elif b < 600000:
            efficiencies.append(0.8 + 0.1 * (b - 500000) / 100000)
        elif b < 700000:
            efficiencies.append(0.95 + 0.03 * (b - 600000) / 100000)
        else:
            efficiencies.append(min(1.0, 0.98 + 0.02 * (b - 700000) / 100000))

    # Generate project selections (cumulative as budget increases)
    project_selections = []
    base_projects = []
    for i, b in enumerate(budgets):
        if b >= 350000 and 'Xingg Lights (Ryż.)' not in base_projects:
            base_projects.append('Xingg Lights (Ryż.)')
        if b >= 380000 and 'Xing Lights (Pop.)' not in base_projects:
            base_projects.append('Xing Lights (Pop.)')
        if b >= 420000 and 'Historical Plaques' not in base_projects:
            base_projects.append('Historical Plaques')
        if b >= 460000 and 'Memory Game' not in base_projects:
            base_projects.append('Memory Game')
        if b >= 500000 and 'Bird Feeding Guide' not in base_projects:
            base_projects.append('Bird Feeding Guide')
        if b >= 540000 and 'Bird Houses' not in base_projects:
            base_projects.append('Bird Houses')
        if b >= 580000 and 'Parent Education' not in base_projects:
            base_projects.append('Parent Education')
        if b >= 620000 and 'Outdoor Chess' not in base_projects:
            base_projects.append('Outdoor Chess')
        if b >= 660000 and 'Tree Protection' not in base_projects:
            base_projects.append('Tree Protection')
        if b >= 700000 and 'Sports Field' not in base_projects:
            base_projects.append('Sports Field')
        if b >= 740000 and 'Cycling Infra.' not in base_projects:
            base_projects.append('Cycling Infra.')
        if b >= 780000 and 'Playgrounds' not in base_projects:
            base_projects.append('Playgrounds')

        project_selections.append(base_projects.copy())

    return {
        'budgets': budgets,
        'efficiencies': efficiencies,
        'project_selections': project_selections,
        'project_names': project_names,
        'title': 'Stare Implementation Case Study',
        'location': 'Stare, Poland'
    }


def generate_comparison_data() -> Dict:
    """
    Generate sample data for Figure 2 (MES vs EES scatter plots).

    Returns:
        Dictionary with MES and EES efficiencies for cardinal and cost utilities
    """
    np.random.seed(42)
    n_instances = 250

    # Cardinal utilities - EES slightly better on average
    mes_cardinal = np.random.beta(8, 2, n_instances) * 0.5 + 0.4  # Range ~0.4-0.9
    ees_cardinal = mes_cardinal + np.random.normal(0, 0.05, n_instances)
    ees_cardinal = np.clip(ees_cardinal, 0.3, 1.0)

    # Cost utilities - MES slightly better on average
    mes_cost = np.random.beta(9, 2, n_instances) * 0.5 + 0.4
    ees_cost = mes_cost + np.random.normal(-0.02, 0.05, n_instances)
    ees_cost = np.clip(ees_cost, 0.3, 1.0)

    return {
        'cardinal': {
            'mes': mes_cardinal.tolist(),
            'ees': ees_cardinal.tolist(),
            'title': 'Comparing EES and MES with Cardinal Utilities'
        },
        'cost': {
            'mes': mes_cost.tolist(),
            'ees': ees_cost.tolist(),
            'title': 'Comparing EES and MES with Cost Utilities'
        }
    }


def generate_execution_comparison_data() -> Dict:
    """
    Generate sample data for Figure 3 (execution comparison bar charts).

    Returns:
        Dictionary with execution counts and efficiencies for each method
    """
    # Data from Table 1 and Table 2 in the paper
    return {
        'executions': {
            'MES + ADD-ONE': {'cardinal': 535.4, 'cost': 465.6},
            'ADD-OPT EES': {'cardinal': 279.6, 'cost': 432.7},
            'ADD-OPT-SKIP': {'cardinal': 27.9, 'cost': 12.4},
            'MAX': {'cardinal': 563.3, 'cost': 478.0}
        },
        'efficiency': {
            'MES + ADD-ONE': {'cardinal': 0.855, 'cost': 0.900},
            'ADD-OPT EES': {'cardinal': 0.848, 'cost': 0.881},
            'ADD-OPT-SKIP': {'cardinal': 0.853, 'cost': 0.855},
            'MAX': {'cardinal': 0.871, 'cost': 0.909}
        }
    }


def generate_non_monotonic_data() -> Dict:
    """
    Generate sample data for Figure 4 (non-monotonic instances).

    Returns:
        Dictionary with executions and efficiency for non-monotonic cases
    """
    return {
        'executions': {
            'MES + Add-One': {'cost': 350, 'cardinal': 280},
            'EES + Complete Add-Opt-Skip': {'cost': 45, 'cardinal': 35}
        },
        'efficiency': {
            'MES + Add-One': {'cost': 0.78, 'cardinal': 0.78},
            'EES + Complete Add-Opt-Skip': {'cost': 0.86, 'cardinal': 0.90}
        }
    }


def generate_dataset_statistics() -> Dict:
    """
    Generate sample data for Figure 7 (dataset characteristics).
    Based on Pabulib dataset statistics from the paper.

    Returns:
        Dictionary with voters, projects, and budgets arrays
    """
    np.random.seed(42)
    n_instances = 250

    # Number of voters - log-normal distribution
    # From paper: 25th: 750, 50th: 1601, 75th: 3703, 90th: 7635, max: 95899
    voters = np.random.lognormal(mean=7.5, sigma=1.0, size=n_instances)
    voters = np.clip(voters, 50, 100000).astype(int)

    # Number of projects - from paper: 25th: 11, 50th: 18, 75th: 36, 90th: 72, max: 138
    projects = np.random.lognormal(mean=3.0, sigma=0.7, size=n_instances)
    projects = np.clip(projects, 5, 150).astype(int)

    # Budget amounts - from paper: 25th: 446914, 50th: 776314, 75th: 1300000, 90th: 3906234
    budgets = np.random.lognormal(mean=13.5, sigma=0.8, size=n_instances)
    budgets = np.clip(budgets, 100000, 35000000).astype(int)

    # Correlation between voters and budget (from paper: 0.84)
    # Adjust budgets to correlate with voters
    budgets = budgets * 0.5 + voters * 200 + np.random.normal(0, 100000, n_instances)
    budgets = np.clip(budgets, 100000, 35000000).astype(int)

    return {
        'voters': voters.tolist(),
        'projects': projects.tolist(),
        'budgets': budgets.tolist(),
        'percentiles': {
            'voters': {25: 750, 50: 1601, 75: 3703, 90: 7635},
            'projects': {25: 11, 50: 18, 75: 36, 90: 72},
            'budgets': {25: 446914, 50: 776314, 75: 1300000, 90: 3906234}
        }
    }


def generate_raw_comparison_data() -> Dict:
    """
    Generate sample data for Figures 8 & 9 (raw MES vs EES without completion).

    Returns:
        Dictionary with MES and EES raw efficiencies
    """
    np.random.seed(43)
    n_instances = 250

    # Without completion methods, MES performs better
    mes_cardinal = np.random.beta(6, 3, n_instances) * 0.5 + 0.2
    ees_cardinal = mes_cardinal * 0.85 + np.random.normal(0, 0.05, n_instances)
    ees_cardinal = np.clip(ees_cardinal, 0.1, 0.8)

    mes_cost = np.random.beta(7, 3, n_instances) * 0.5 + 0.3
    ees_cost = mes_cost * 0.8 + np.random.normal(0, 0.05, n_instances)
    ees_cost = np.clip(ees_cost, 0.1, 0.8)

    return {
        'cardinal': {
            'mes': mes_cardinal.tolist(),
            'ees': ees_cardinal.tolist(),
            'title': 'Comparing EES and MES with Cardinal Utilities (No Completion)'
        },
        'cost': {
            'mes': mes_cost.tolist(),
            'ees': ees_cost.tolist(),
            'title': 'Comparing EES and MES with Cost Utilities (No Completion)'
        }
    }


def generate_add_opt_skip_comparison_data() -> Dict:
    """
    Generate sample data for Figures 5 & 6 (ADD-OPT-SKIP vs ADD-ONE).

    Returns:
        Dictionary with EES ADD-OPT-SKIP and MES ADD-ONE efficiencies
    """
    np.random.seed(44)
    n_instances = 250

    # Cardinal utilities
    mes_cardinal = np.random.beta(9, 2, n_instances) * 0.5 + 0.4
    ees_cardinal = mes_cardinal + np.random.normal(0.01, 0.04, n_instances)
    ees_cardinal = np.clip(ees_cardinal, 0.3, 1.0)

    # Cost utilities
    mes_cost = np.random.beta(10, 2, n_instances) * 0.5 + 0.4
    ees_cost = mes_cost + np.random.normal(-0.03, 0.05, n_instances)
    ees_cost = np.clip(ees_cost, 0.3, 1.0)

    return {
        'cardinal': {
            'mes': mes_cardinal.tolist(),
            'ees': ees_cardinal.tolist(),
            'title': 'EES ADD-OPT-SKIP vs MES ADD-ONE (Cardinal)'
        },
        'cost': {
            'mes': mes_cost.tolist(),
            'ees': ees_cost.tolist(),
            'title': 'EES ADD-OPT-SKIP vs MES ADD-ONE (Cost)'
        }
    }


def get_all_sample_data() -> Dict:
    """
    Generate all sample data for all figures.

    Returns:
        Dictionary containing all sample data keyed by figure number
    """
    return {
        'figure_1': generate_stare_wlochy_data(),
        'figure_2': generate_comparison_data(),
        'figure_3': generate_execution_comparison_data(),
        'figure_4': generate_non_monotonic_data(),
        'figures_5_6': generate_add_opt_skip_comparison_data(),
        'figure_7': generate_dataset_statistics(),
        'figures_8_9': generate_raw_comparison_data(),
        'figure_10': generate_stare_implementation_data()
    }
