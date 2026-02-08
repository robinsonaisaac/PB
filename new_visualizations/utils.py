from typing import List, Dict

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
