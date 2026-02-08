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
