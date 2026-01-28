"""
Completion Heuristics for EES

From "Streamlining Equal Shares" (arXiv:2502.11797), Section 6.2.

Implements:
- ADD-ONE: Increase budget by n (i.e., +1 per voter) until overspending
- ADD-OPT: Use optimal budget increment from ADD-OPT algorithm
- ADD-OPT-SKIP: Like ADD-OPT but only consider unselected projects

Each has a "complete" variant that continues until all projects are selected,
then returns the feasible outcome with highest spending efficiency.
"""

from fractions import Fraction
from typing import Callable, List, Optional, Tuple

from .types import Election, EESOutcome, Project
from .ees import ees_with_outcome
from .add_opt_cardinal import add_opt_cardinal
from .add_opt_uniform import add_opt_uniform
from .gpc_cardinal import greedy_project_change_cardinal
from .gpc_uniform import greedy_project_change_uniform, compute_L_lists


def add_one_completion(
    election: Election,
    utility: Callable[[Project], Fraction],
) -> EESOutcome:
    """
    ADD-ONE completion: increase budget by n per iteration until overspending.
    
    Returns the last feasible outcome before overspending.
    """
    actual_budget = election.budget
    n = election.n
    
    current_budget = election.budget
    best_outcome: Optional[EESOutcome] = None
    
    while True:
        e = election.with_budget(current_budget)
        outcome = ees_with_outcome(e, utility)
        
        if outcome.total_cost > actual_budget:
            # Overspending, return previous outcome
            break
        
        best_outcome = outcome
        
        if len(outcome.selected) == election.m:
            # All projects selected
            break
        
        # Increase budget by n (i.e., +1 per voter)
        current_budget += n
    
    if best_outcome is None:
        # Edge case: even initial budget causes overspending
        return ees_with_outcome(election, utility)
    
    return best_outcome


def add_opt_completion(
    election: Election,
    utility: Callable[[Project], Fraction],
    is_cardinal: bool = True,
) -> EESOutcome:
    """
    ADD-OPT completion: use optimal budget increment until overspending.
    
    Returns the last feasible outcome before overspending.
    """
    actual_budget = election.budget
    n = election.n
    
    current_budget = election.budget
    best_outcome: Optional[EESOutcome] = None
    
    while True:
        e = election.with_budget(current_budget)
        outcome = ees_with_outcome(e, utility)
        
        if outcome.total_cost > actual_budget:
            break
        
        best_outcome = outcome
        
        if len(outcome.selected) == election.m:
            break
        
        # Compute optimal increment
        if is_cardinal:
            d = add_opt_cardinal(e, outcome)
        else:
            d = add_opt_uniform(e, outcome, utility)
        
        if d is None:  # Infinity
            break
        
        current_budget += n * d
    
    if best_outcome is None:
        return ees_with_outcome(election, utility)
    
    return best_outcome


def add_opt_skip_completion(
    election: Election,
    utility: Callable[[Project], Fraction],
    is_cardinal: bool = True,
) -> EESOutcome:
    """
    ADD-OPT-SKIP completion: like ADD-OPT but only consider unselected projects.
    
    This is more efficient and continues until all projects are considered.
    Returns the feasible outcome with highest spending efficiency.
    """
    actual_budget = election.budget
    n = election.n
    
    current_budget = election.budget
    all_outcomes: List[Tuple[Fraction, EESOutcome]] = []  # (efficiency, outcome)
    
    while True:
        e = election.with_budget(current_budget)
        outcome = ees_with_outcome(e, utility)
        
        # Record if feasible
        if outcome.total_cost <= actual_budget:
            eff = outcome.spending_efficiency(actual_budget)
            all_outcomes.append((eff, outcome))
        
        if len(outcome.selected) == election.m:
            break
        
        # Compute increment only for unselected projects
        d: Optional[Fraction] = None  # None = infinity
        
        if is_cardinal:
            for p_id in election.projects:
                if p_id not in outcome.selected:
                    gpc_d = greedy_project_change_cardinal(e, outcome, p_id)
                    if gpc_d is not None and gpc_d > 0:
                        if d is None or gpc_d < d:
                            d = gpc_d
        else:
            L_lists = compute_L_lists(e, outcome, utility)
            for p_id in election.projects:
                if p_id not in outcome.selected:
                    gpc_d = greedy_project_change_uniform(
                        e, outcome, p_id, utility, L_lists
                    )
                    if gpc_d is not None and gpc_d > 0:
                        if d is None or gpc_d < d:
                            d = gpc_d
        
        if d is None:  # Infinity
            break
        
        current_budget += n * d
    
    if not all_outcomes:
        return ees_with_outcome(election, utility)
    
    # Return outcome with highest efficiency
    all_outcomes.sort(key=lambda x: x[0], reverse=True)
    return all_outcomes[0][1]


def add_one_complete(
    election: Election,
    utility: Callable[[Project], Fraction],
) -> EESOutcome:
    """
    ADD-ONE (complete): continue until all projects selected,
    then return feasible outcome with highest efficiency.
    """
    actual_budget = election.budget
    n = election.n
    
    current_budget = election.budget
    all_outcomes: List[Tuple[Fraction, EESOutcome]] = []
    
    while True:
        e = election.with_budget(current_budget)
        outcome = ees_with_outcome(e, utility)
        
        if outcome.total_cost <= actual_budget:
            eff = outcome.spending_efficiency(actual_budget)
            all_outcomes.append((eff, outcome))
        
        if len(outcome.selected) == election.m:
            break
        
        current_budget += n
    
    if not all_outcomes:
        return ees_with_outcome(election, utility)
    
    all_outcomes.sort(key=lambda x: x[0], reverse=True)
    return all_outcomes[0][1]


def add_opt_complete(
    election: Election,
    utility: Callable[[Project], Fraction],
    is_cardinal: bool = True,
) -> EESOutcome:
    """
    ADD-OPT (complete): continue until all projects selected,
    then return feasible outcome with highest efficiency.
    """
    actual_budget = election.budget
    n = election.n
    
    current_budget = election.budget
    all_outcomes: List[Tuple[Fraction, EESOutcome]] = []
    
    while True:
        e = election.with_budget(current_budget)
        outcome = ees_with_outcome(e, utility)
        
        if outcome.total_cost <= actual_budget:
            eff = outcome.spending_efficiency(actual_budget)
            all_outcomes.append((eff, outcome))
        
        if len(outcome.selected) == election.m:
            break
        
        if is_cardinal:
            d = add_opt_cardinal(e, outcome)
        else:
            d = add_opt_uniform(e, outcome, utility)
        
        if d is None:  # Infinity
            break
        
        current_budget += n * d
    
    if not all_outcomes:
        return ees_with_outcome(election, utility)
    
    all_outcomes.sort(key=lambda x: x[0], reverse=True)
    return all_outcomes[0][1]


def add_opt_skip_complete(
    election: Election,
    utility: Callable[[Project], Fraction],
    is_cardinal: bool = True,
) -> EESOutcome:
    """
    ADD-OPT-SKIP (complete): same as add_opt_skip_completion.
    
    The SKIP variant already continues until all projects are considered.
    """
    return add_opt_skip_completion(election, utility, is_cardinal)
