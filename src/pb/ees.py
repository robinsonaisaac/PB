"""
Algorithm 1: Exact Equal Shares (EES)

From "Streamlining Equal Shares" (arXiv:2502.11797).

EES selects projects by highest bang-per-buck, where:
- bang-per-buck = u(p) * |paying_voters| / cost(p)
- Only voters who can afford cost(p)/|supporters| contribute equally
- Ties broken lexicographically by project id (larger id wins)
"""

from fractions import Fraction
from typing import Callable, Dict, List, Optional, Set, Tuple
from collections import OrderedDict

from .types import Election, EESOutcome, Project


def ees(
    election: Election,
    utility: Callable[[Project], Fraction] = lambda p: Fraction(1),
) -> Set[str]:
    """
    Run EES and return the set of selected project ids.
    
    Args:
        election: The election E(b)
        utility: Utility function u(p). Default is cardinal (u(p)=1).
                 For cost utilities, use: lambda p: p.cost
    
    Returns:
        Set of selected project ids
    """
    outcome = ees_with_outcome(election, utility)
    return outcome.selected


def ees_with_outcome(
    election: Election,
    utility: Callable[[Project], Fraction] = lambda p: Fraction(1),
) -> EESOutcome:
    """
    Run EES and return full outcome including payments and auxiliary info.
    
    This implements Algorithm 1 from the paper.
    
    Args:
        election: The election E(b)
        utility: Utility function u(p). Default is cardinal (u(p)=1).
    
    Returns:
        EESOutcome with selected projects, payments, leftover budgets,
        and selection order (for ADD-OPT algorithms).
    """
    n = election.n
    budget = election.budget
    
    # Initialize voter budgets: each voter gets b/n
    voter_budgets: Dict[int, Fraction] = {
        v: budget / n for v in election.voters
    }
    
    # Payment matrix: (voter_id, project_id) -> payment amount
    payments: Dict[Tuple[int, str], Fraction] = {}
    
    # Track selected projects and their selection order
    selected: Set[str] = set()
    selection_order: List[Tuple[str, Fraction]] = []
    total_cost = Fraction(0)
    
    # Precompute supporters for each project
    supporters: Dict[str, Set[int]] = {
        p_id: election.project_supporters(p_id)
        for p_id in election.projects
    }
    
    while True:
        best_project_id: Optional[str] = None
        best_bpb = Fraction(0)
        best_payers: List[int] = []
        best_contribution = Fraction(0)
        
        for p_id, project in election.projects.items():
            if p_id in selected:
                continue
            
            supp = supporters[p_id]
            if not supp:
                continue
            
            # Sort supporters by their current budget (ascending)
            supp_sorted = sorted(supp, key=lambda v: voter_budgets[v])
            
            # Find the largest group that can afford to share the cost equally
            # We iterate from poorest to richest, removing voters who can't afford
            num_paying = len(supp_sorted)
            for i, voter in enumerate(supp_sorted):
                contribution = project.cost / num_paying
                if contribution <= voter_budgets[voter]:
                    # This voter and all richer ones can afford it
                    payers = supp_sorted[i:]
                    bpb = utility(project) * len(payers) / project.cost
                    
                    # Check if this is better than current best
                    # Tie-break by larger project id
                    if bpb > best_bpb or (bpb == best_bpb and best_project_id is not None and p_id > best_project_id):
                        best_bpb = bpb
                        best_project_id = p_id
                        best_payers = payers
                        best_contribution = contribution
                    break
                num_paying -= 1
        
        if best_project_id is None:
            # No more projects can be funded
            break
        
        # Fund the best project
        project = election.projects[best_project_id]
        for voter in best_payers:
            voter_budgets[voter] -= best_contribution
            payments[(voter, best_project_id)] = best_contribution
        
        selected.add(best_project_id)
        selection_order.append((best_project_id, best_bpb))
        total_cost += project.cost
    
    return EESOutcome(
        selected=selected,
        payments=payments,
        leftover_budgets=voter_budgets,
        selection_order=selection_order,
        total_cost=total_cost,
    )


def cardinal_utility(p: Project) -> Fraction:
    """Cardinal/approval utility: u(p) = 1."""
    return Fraction(1)


def cost_utility(p: Project) -> Fraction:
    """Cost utility: u(p) = cost(p)."""
    return p.cost

