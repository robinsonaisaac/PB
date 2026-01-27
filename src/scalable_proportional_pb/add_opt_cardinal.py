"""
Algorithm 3: ADD-OPT for Cardinal Utilities

From "Streamlining Equal Shares" (arXiv:2502.11797), Section 4.

ADD-OPT computes the minimum per-voter budget increase d such that
EES(E(b + n*d)) ≠ (W, X).

This algorithm runs in O(mn) time.
"""

from fractions import Fraction
from typing import Callable, Optional

from .types import Election, EESOutcome, Project
from .gpc_cardinal import greedy_project_change_cardinal


def add_opt_cardinal(
    election: Election,
    outcome: EESOutcome,
) -> Optional[Fraction]:
    """
    Algorithm 3: ADD-OPT for cardinal utilities.
    
    Computes the minimum d > 0 such that EES(E(b + n*d)) ≠ (W, X).
    
    Args:
        election: The election E(b)
        outcome: The EES outcome (W, X) for E(b)
        
    Returns:
        The minimum d value, or None if outcome is stable for all budgets (infinity).
    """
    d: Optional[Fraction] = None  # None means infinity
    
    for project_id in election.projects:
        gpc_d = greedy_project_change_cardinal(election, outcome, project_id)
        if gpc_d is not None and gpc_d > 0:
            if d is None or gpc_d < d:
                d = gpc_d
    
    return d
