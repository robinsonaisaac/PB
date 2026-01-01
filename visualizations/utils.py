"""
Utility functions for parsing and processing participatory budgeting results.
"""

import re
from fractions import Fraction
from typing import Union, List, Dict, Optional


def parse_fraction(s: Union[str, float, int]) -> float:
    """
    Parse a fraction string to float.

    Args:
        s: Fraction string like "406/447" or numeric value

    Returns:
        Float value of the fraction

    Examples:
        >>> parse_fraction("406/447")
        0.9082774049217002
        >>> parse_fraction("1")
        1.0
        >>> parse_fraction(0.5)
        0.5
    """
    if isinstance(s, (int, float)):
        return float(s)

    s = str(s).strip()

    if '/' in s:
        try:
            return float(Fraction(s))
        except (ValueError, ZeroDivisionError):
            # Try parsing as two numbers
            parts = s.split('/')
            if len(parts) == 2:
                return float(parts[0]) / float(parts[1])

    try:
        return float(s)
    except ValueError:
        return 0.0


def parse_project_list(s: str) -> List[str]:
    """
    Parse a project list string to a Python list.

    Args:
        s: String like "[W061AN, W007AN, W046AN]" or "['W061AN', 'W007AN']"

    Returns:
        List of project IDs

    Examples:
        >>> parse_project_list("[W061AN, W007AN, W046AN]")
        ['W061AN', 'W007AN', 'W046AN']
    """
    if not s or s == '[]':
        return []

    s = str(s).strip()

    # Remove outer brackets
    if s.startswith('[') and s.endswith(']'):
        s = s[1:-1]

    # Handle empty
    if not s.strip():
        return []

    # Split by comma and clean up each item
    items = []
    for item in s.split(','):
        item = item.strip()
        # Remove quotes if present
        item = item.strip("'\"")
        if item:
            items.append(item)

    return items


def parse_ordered_dict(s: str) -> Dict[str, float]:
    """
    Parse an OrderedDict string with mpq fractions to a dictionary.

    Args:
        s: String like "OrderedDict([(W046AN, mpq(500,1)), (W090AN, mpq(478,1))])"

    Returns:
        Dictionary mapping project IDs to their values

    Examples:
        >>> parse_ordered_dict("OrderedDict([(W046AN, mpq(500,1)), (W090AN, mpq(478,1))])")
        {'W046AN': 500.0, 'W090AN': 478.0}
    """
    if not s or 'OrderedDict' not in str(s):
        # If it's just a list, return empty dict
        return {}

    s = str(s).strip()

    result = {}

    # Pattern to match: (ProjectID, mpq(num,denom)) or (ProjectID, value)
    pattern = r'\(([^,]+),\s*mpq\((\d+),(\d+)\)\)'
    matches = re.findall(pattern, s)

    for match in matches:
        project_id = match[0].strip()
        numerator = float(match[1])
        denominator = float(match[2])
        value = numerator / denominator if denominator != 0 else 0
        result[project_id] = value

    # If no mpq pattern found, try simple value pattern
    if not result:
        simple_pattern = r'\(([^,]+),\s*([^\)]+)\)'
        matches = re.findall(simple_pattern, s)
        for match in matches:
            project_id = match[0].strip()
            try:
                value = float(match[1].strip())
                result[project_id] = value
            except ValueError:
                pass

    return result


def calculate_efficiency(total_cost: float, budget: float) -> float:
    """
    Calculate spending efficiency.

    Args:
        total_cost: Total cost of selected projects
        budget: Available budget

    Returns:
        Efficiency ratio (0.0 to 1.0+)
    """
    if budget <= 0:
        return 0.0
    return total_cost / budget


def extract_efficiency_from_row(row: dict, efficiency_col: str = 'efficiency') -> float:
    """
    Extract efficiency value from a data row, handling various column names.

    Args:
        row: Dictionary representing a row of data
        efficiency_col: Primary column name to look for

    Returns:
        Efficiency as float
    """
    # Try different column names
    columns_to_try = [
        efficiency_col,
        'highest_efficiency_attained',
        'final_efficiency',
        'efficiency'
    ]

    for col in columns_to_try:
        if col in row and row[col]:
            return parse_fraction(row[col])

    return 0.0


def extract_projects_from_row(row: dict, projects_col: str = 'selected_projects') -> List[str]:
    """
    Extract project list from a data row, handling various column names.

    Args:
        row: Dictionary representing a row of data
        projects_col: Primary column name to look for

    Returns:
        List of project IDs
    """
    # Try different column names
    columns_to_try = [
        projects_col,
        'most_efficient_project_set',
        'final_project_set',
        'selected_projects'
    ]

    for col in columns_to_try:
        if col in row and row[col]:
            val = row[col]
            if 'OrderedDict' in str(val):
                return list(parse_ordered_dict(val).keys())
            else:
                return parse_project_list(val)

    return []


def compare_efficiencies(eff1: float, eff2: float, tolerance: float = 1e-6) -> str:
    """
    Compare two efficiency values.

    Args:
        eff1: First efficiency (e.g., MES)
        eff2: Second efficiency (e.g., EES)
        tolerance: Tolerance for considering values equal

    Returns:
        'first', 'second', or 'equal'
    """
    diff = eff1 - eff2
    if abs(diff) < tolerance:
        return 'equal'
    elif diff > 0:
        return 'first'
    else:
        return 'second'


def calculate_percentages(comparisons: List[str]) -> Dict[str, float]:
    """
    Calculate percentage breakdown of comparison results.

    Args:
        comparisons: List of comparison results ('first', 'second', 'equal')

    Returns:
        Dictionary with percentages for each category
    """
    if not comparisons:
        return {'first': 0.0, 'second': 0.0, 'equal': 0.0}

    total = len(comparisons)
    counts = {'first': 0, 'second': 0, 'equal': 0}

    for comp in comparisons:
        if comp in counts:
            counts[comp] += 1

    return {
        'first': (counts['first'] / total) * 100,
        'second': (counts['second'] / total) * 100,
        'equal': (counts['equal'] / total) * 100
    }


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
