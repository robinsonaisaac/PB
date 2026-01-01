"""
Data loading functions for participatory budgeting results.
"""

import os
import csv
from pathlib import Path
from typing import Dict, List, Optional, Union
import pandas as pd

from .utils import (
    parse_fraction,
    parse_project_list,
    parse_ordered_dict,
    extract_instance_info,
    extract_efficiency_from_row,
    extract_projects_from_row
)


def load_single_result(csv_path: str) -> Dict:
    """
    Load a single result CSV file.

    Args:
        csv_path: Path to the CSV file

    Returns:
        Dictionary with parsed result data
    """
    result = {
        'filepath': csv_path,
        'filename': os.path.basename(csv_path),
        'instance_info': extract_instance_info(os.path.basename(csv_path))
    }

    try:
        with open(csv_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            rows = list(reader)

            if rows:
                row = rows[0]  # Usually only one data row

                # Extract efficiency
                result['efficiency'] = extract_efficiency_from_row(row)

                # Extract projects
                result['projects'] = extract_projects_from_row(row)

                # Extract budget increase count
                if 'budget_increase_count' in row:
                    try:
                        result['budget_increase_count'] = int(row['budget_increase_count'])
                    except (ValueError, TypeError):
                        result['budget_increase_count'] = 0

                # Extract other fields
                for field in ['max_budget_increase', 'min_budget_increase', 'avg_budget_increase']:
                    if field in row and row[field]:
                        result[field] = parse_fraction(row[field])

                # Monotonic violation
                if 'monotonic_violation' in row:
                    result['monotonic_violation'] = str(row['monotonic_violation']) == '1'

                # Store raw data for additional fields
                if 'most_efficient_project_set' in row:
                    result['most_efficient_project_set'] = extract_projects_from_row(
                        {'most_efficient_project_set': row['most_efficient_project_set']}
                    )

                if 'highest_efficiency_attained' in row:
                    result['highest_efficiency'] = parse_fraction(row['highest_efficiency_attained'])

                if 'final_project_set' in row:
                    result['final_project_set'] = extract_projects_from_row(
                        {'final_project_set': row['final_project_set']}
                    )

                if 'final_efficiency' in row:
                    result['final_efficiency'] = parse_fraction(row['final_efficiency'])

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

    Args:
        results_root: Path to the results/ folder

    Returns:
        Nested dictionary with structure:
        {
            'exact_equal_shares': {
                'approval': {
                    'exhaustive': DataFrame,
                    'exhaustive_heuristic': DataFrame,
                    'non_exhaustive': DataFrame,
                    'non_exhaustive_heuristic': DataFrame
                },
                'cost': {
                    'exhaustive': DataFrame,
                    'non_exhaustive': DataFrame
                }
            },
            'waterflow_equal_shares': {...}
        }
    """
    results = {}
    root = Path(results_root)

    # Define expected structure
    structure = {
        'exact_equal_shares': {
            'approval': ['exhaustive', 'exhaustive_heuristic', 'non_exhaustive', 'non_exhaustive_heuristic'],
            'cost': ['exhaustive', 'non_exhaustive']
        },
        'waterflow_equal_shares': {
            'approval': ['exhaustive', 'non_exhaustive'],
            'cost': ['exhaustive', 'non_exhaustive']
        }
    }

    for method, utilities in structure.items():
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


def aggregate_for_comparison(results: Dict, method1: str = 'exact_equal_shares',
                              method2: str = 'waterflow_equal_shares',
                              utility: str = 'approval',
                              variant: str = 'exhaustive') -> pd.DataFrame:
    """
    Aggregate results from two methods for comparison plots.

    Args:
        results: Results dictionary from load_all_results
        method1: First method name
        method2: Second method name
        utility: 'approval' or 'cost'
        variant: 'exhaustive', 'non_exhaustive', etc.

    Returns:
        DataFrame with columns for both methods' efficiencies
    """
    df1 = results.get(method1, {}).get(utility, {}).get(variant, pd.DataFrame())
    df2 = results.get(method2, {}).get(utility, {}).get(variant, pd.DataFrame())

    if df1.empty or df2.empty:
        return pd.DataFrame()

    # Merge on filename (same instance)
    merged = pd.merge(
        df1[['filename', 'efficiency', 'budget_increase_count']],
        df2[['filename', 'efficiency', 'budget_increase_count']],
        on='filename',
        suffixes=('_1', '_2')
    )

    return merged


def get_efficiency_statistics(df: pd.DataFrame,
                                efficiency_col: str = 'efficiency') -> Dict[str, float]:
    """
    Calculate statistics for efficiency values.

    Args:
        df: DataFrame with efficiency column
        efficiency_col: Name of efficiency column

    Returns:
        Dictionary with mean, median, std, min, max
    """
    if df.empty or efficiency_col not in df.columns:
        return {}

    efficiencies = df[efficiency_col].dropna()

    return {
        'mean': efficiencies.mean(),
        'median': efficiencies.median(),
        'std': efficiencies.std(),
        'min': efficiencies.min(),
        'max': efficiencies.max(),
        'count': len(efficiencies)
    }


def get_execution_statistics(df: pd.DataFrame,
                               count_col: str = 'budget_increase_count') -> Dict[str, float]:
    """
    Calculate statistics for execution counts.

    Args:
        df: DataFrame with count column
        count_col: Name of count column

    Returns:
        Dictionary with mean, median, std
    """
    if df.empty or count_col not in df.columns:
        return {}

    counts = df[count_col].dropna()

    return {
        'mean': counts.mean(),
        'median': counts.median(),
        'std': counts.std(),
        'count': len(counts)
    }


def load_test_instance(results_root: str) -> Dict:
    """
    Load the test_instance.csv file.

    Args:
        results_root: Path to results folder

    Returns:
        Dictionary with test instance data
    """
    test_path = Path(results_root) / 'test_instance.csv'
    if test_path.exists():
        return load_single_result(str(test_path))
    return {}


def get_instance_names(results: Dict) -> List[str]:
    """
    Get list of unique instance names across all results.

    Args:
        results: Results dictionary from load_all_results

    Returns:
        List of unique instance names
    """
    names = set()

    for method_data in results.values():
        for utility_data in method_data.values():
            for variant_df in utility_data.values():
                if isinstance(variant_df, pd.DataFrame) and not variant_df.empty:
                    if 'filename' in variant_df.columns:
                        names.update(variant_df['filename'].tolist())

    return sorted(list(names))


def filter_by_location(df: pd.DataFrame, city: str = None,
                        year: str = None, country: str = None) -> pd.DataFrame:
    """
    Filter results by location.

    Args:
        df: Results DataFrame
        city: City name filter
        year: Year filter
        country: Country filter

    Returns:
        Filtered DataFrame
    """
    if df.empty:
        return df

    # Ensure instance_info is extracted
    if 'instance_info' not in df.columns:
        return df

    mask = pd.Series([True] * len(df))

    if city:
        mask &= df['instance_info'].apply(lambda x: x.get('city', '').lower() == city.lower())
    if year:
        mask &= df['instance_info'].apply(lambda x: x.get('year', '') == str(year))
    if country:
        mask &= df['instance_info'].apply(lambda x: x.get('country', '').lower() == country.lower())

    return df[mask]
