"""
Data loading functions for participatory budgeting results.
"""

import os
import csv
from pathlib import Path
from typing import Dict
import pandas as pd


def extract_instance_info(filename: str) -> Dict[str, str]:
    """
    Extract location and year information from filename.

    Args:
        filename: Filename like "poland_lodz_2020_andrzejow.csv"

    Returns:
        Dictionary with country, city, year, district
    """
    # Remove .csv extension
    name = filename.replace('.csv', '')

    parts = name.split('_')

    result = {
        'country': parts[0] if len(parts) > 0 else '',
        'city': parts[1] if len(parts) > 1 else '',
        'year': parts[2] if len(parts) > 2 else '',
        'district': '_'.join(parts[3:]) if len(parts) > 3 else ''
    }

    return result


def load_single_result(csv_path: str) -> Dict:
    """
    Load a single result CSV file.

    The CSV files contain:
    - most_efficient_project_set: List of projects in the most efficient set
    - highest_efficiency_attained: Maximum efficiency value achieved
    - budget_increase_list: List of budget increases at each step
    - efficiency_list: List of efficiency values at each step

    Args:
        csv_path: Path to the CSV file

    Returns:
        Dictionary with parsed result data
    """
    result = {
        'filepath': csv_path,
        'election_name': os.path.splitext(os.path.basename(csv_path))[0],
        'instance_info': extract_instance_info(os.path.basename(csv_path))
    }

    try:
        with open(csv_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            rows = list(reader)

            if rows:
                row = rows[0]  # Usually only one data row

                # Extract most efficient project set (list of project IDs)
                if 'most_efficient_project_set' in row and row['most_efficient_project_set']:
                    try:
                        # Parse as Python list from string representation
                        import ast
                        result['most_efficient_project_set'] = ast.literal_eval(row['most_efficient_project_set'])
                    except (ValueError, SyntaxError):
                        result['most_efficient_project_set'] = []

                # Extract highest efficiency attained (single float)
                if 'highest_efficiency_attained' in row and row['highest_efficiency_attained']:
                    try:
                        result['highest_efficiency_attained'] = float(row['highest_efficiency_attained'])
                    except (ValueError, TypeError):
                        pass

                # Extract budget increase list (list of numbers/fractions)
                if 'budget_increase_list' in row and row['budget_increase_list']:
                    try:
                        import ast
                        # Parse the list representation, then convert Fraction strings to floats
                        budget_list_raw = ast.literal_eval(row['budget_increase_list'])
                        budget_list = []
                        for item in budget_list_raw:
                            if isinstance(item, str) and 'Fraction' in item:
                                # Parse Fraction objects
                                from fractions import Fraction
                                frac = Fraction(item.split('Fraction(')[1].split(')')[0])
                                budget_list.append(float(frac))
                            else:
                                budget_list.append(float(item))
                        result['budget_increase_list'] = budget_list
                        result['budget_increase_count'] = len(budget_list)
                    except (ValueError, TypeError, IndexError):
                        result['budget_increase_list'] = []
                        result['budget_increase_count'] = 0

                # Extract efficiency list (list of floats)
                if 'efficiency_list' in row and row['efficiency_list']:
                    try:
                        import ast
                        eff_list = ast.literal_eval(row['efficiency_list'])
                        # Convert to floats if needed
                        result['efficiency_list'] = [float(e) for e in eff_list]
                    except (ValueError, TypeError):
                        result['efficiency_list'] = []

    except Exception as e:
        result['error'] = str(e)

    return result


def load_results_folder(folder_path: str) -> pd.DataFrame:
    """
    Load all CSV files from a results folder into a DataFrame.

    Args:
        folder_path: Path to folder containing CSV files

    Returns:
        DataFrame with one row per result file
    """
    results = []

    folder = Path(folder_path)
    if not folder.exists():
        return pd.DataFrame()

    for csv_file in folder.glob('*.csv'):
        result = load_single_result(str(csv_file))
        results.append(result)

    if not results:
        return pd.DataFrame()

    df = pd.DataFrame(results)
    return df


def load_all_results(results_root: str) -> Dict[str, Dict]:
    """
    Load all results from the complete results directory structure.

    Supports the new unified CLI directory structure:
    - ees/cardinal/add-opt, mes/cardinal/add-one, ...

    Args:
        results_root: Path to the results/ folder

    Returns:
        Nested dictionary with structure:
        {
            'ees': {
                'cardinal': {
                    'add-opt': DataFrame,
                    'add-one': DataFrame,
                    ...
                },
                'cost': {...}
            },
            'mes': {
                'cardinal': {...},
                'cost': {...}
            }
        }
    """
    results = {}
    root = Path(results_root)

    # New unified CLI structure
    new_structure = {
        'ees': {
            'cardinal': ['none', 'add-one', 'add-opt', 'add-opt-skip',
                         'add-one_exhaustive', 'add-opt_exhaustive', 'add-opt-skip_exhaustive'],
            'cost': ['none', 'add-one', 'add-opt', 'add-opt-skip',
                    'add-one_exhaustive', 'add-opt_exhaustive', 'add-opt-skip_exhaustive']
        },
        'mes': {
            'cardinal': ['none', 'add-one', 'add-one_exhaustive'],
            'cost': ['none', 'add-one', 'add-one_exhaustive']
        }
    }

    for method, utilities in new_structure.items():
        results[method] = {}
        for utility, variants in utilities.items():
            results[method][utility] = {}
            for variant in variants:
                folder_path = root / method / utility / variant
                if folder_path.exists():
                    results[method][utility][variant] = load_results_folder(str(folder_path))
                else:
                    results[method][utility][variant] = pd.DataFrame()

    return results