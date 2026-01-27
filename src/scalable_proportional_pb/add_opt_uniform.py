"""
Algorithm 5: ADD-OPT for Uniform Utilities

From "Streamlining Equal Shares" (arXiv:2502.11797), Section 5.1.

ADD-OPT for uniform utilities computes the minimum per-voter budget increase d
such that EES(E(b + n*d)) ≠ (W, X).

This algorithm runs in O(m²n) time.
"""

from fractions import Fraction
from typing import Callable, Optional

from .types import Election, EESOutcome, Project
from .gpc_uniform import greedy_project_change_uniform, compute_L_lists


def add_opt_uniform(
    election: Election,
    outcome: EESOutcome,
    utility: Callable[[Project], Fraction],
) -> Optional[Fraction]:
    """
    Algorithm 5: ADD-OPT for uniform utilities.
    
    Computes the minimum d > 0 such that EES(E(b + n*d), u) ≠ (W, X).
    
    Args:
        election: The election E(b)
        outcome: The EES outcome (W, X) for E(b) with utility u
        utility: The uniform utility function u(p)
        
    Returns:
        The minimum d value, or None if outcome is stable for all budgets (infinity).
    """
    # Precompute L lists
    L_lists = compute_L_lists(election, outcome, utility)
    
    d: Optional[Fraction] = None  # None means infinity
    
    for project_id in election.projects:
        gpc_d = greedy_project_change_uniform(
            election, outcome, project_id, utility, L_lists
        )
        if gpc_d is not None and gpc_d > 0:
            if d is None or gpc_d < d:
                d = gpc_d
    
    return d
