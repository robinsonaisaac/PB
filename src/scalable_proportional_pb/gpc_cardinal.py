"""
Algorithm 2: GREEDYPROJECTCHANGE for Cardinal Utilities

From "Streamlining Equal Shares" (arXiv:2502.11797), Section 4.1.

Given a stable EES outcome (W, X) and a project p, computes the minimum
per-voter budget increase d such that (p, B) certifies instability of (W, X).

This algorithm runs in O(n) time.
"""

from fractions import Fraction
from typing import Dict, List, Optional, Set, Tuple

from .types import Election, EESOutcome, leximax_gt, leximax_lt


def greedy_project_change_cardinal(
    election: Election,
    outcome: EESOutcome,
    project_id: str,
) -> Optional[Fraction]:
    """
    Algorithm 2: GREEDYPROJECTCHANGE for cardinal utilities.
    
    Computes the minimum d > 0 such that there exists B ⊆ N_p with (p, B)
    certifying instability of (W, X) for E(b + n*d).
    
    Args:
        election: The election E(b)
        outcome: A stable EES outcome (W, X) for E(b)
        project_id: The project p to consider
        
    Returns:
        The minimum d value, or None if p cannot certify instability (infinity).
    """
    project = election.projects[project_id]
    cost = project.cost
    
    # N_p: voters who approve p
    N_p = election.project_supporters(project_id)
    
    # N_p(X): voters already paying for p in outcome
    N_p_X = outcome.project_payers(project_id)
    
    # O_p(X) = N_p \ N_p(X): supporters not currently paying
    O_p_X = N_p - N_p_X
    
    if not O_p_X and not N_p_X:
        # No supporters at all
        return None  # Infinity
    
    if not O_p_X:
        # All supporters already paying, no way to add more
        return None  # Infinity
    
    # Build leftover budgets list: sorted (voter, leftover) for voters in O_p(X)
    leftover_list: List[Tuple[int, Fraction]] = sorted(
        [(v, outcome.leftover_budgets[v]) for v in O_p_X],
        key=lambda x: x[1]
    )
    
    # Build leximax payments list: sorted (voter, leximax_payment) for voters in O_p(X)
    # Sorted by leximax order (ascending).
    # Since leximax_lt prefers Larger IDs (p1 > p2), we must sort such that
    # Larger IDs come before Smaller IDs for equal amounts.
    # Standard string sort is A < B. We want B < A.
    class LeximaxKey:
        def __init__(self, item):
            self.amount = item[1][0]
            self.pid = item[1][1]
        
        def __lt__(self, other):
            if self.amount != other.amount:
                return self.amount < other.amount
            if self.pid is None: return True
            if other.pid is None: return False
            # Invert ID comparison: Larger ID is "smaller/better" in leximax
            return self.pid > other.pid
            
    leximax_list: List[Tuple[int, Tuple[Fraction, Optional[str]]]] = sorted(
        [(v, outcome.leximax_payment(v)) for v in O_p_X],
        key=LeximaxKey
    )
    
    # Initialize d to None (infinity)
    d: Optional[Fraction] = None
    
    # LQ: liquid voters (will pay from leftover budgets)
    # SL: solvent voters (will deviate from another project)
    LQ: Set[int] = set(O_p_X)
    SL: Set[int] = set()
    
    # Pointers
    i = 0  # pointer into leftover_list
    j = 0  # pointer into leximax_list
    
    # B = N_p(X) ∪ LQ ∪ SL
    def get_buyers() -> Set[int]:
        return N_p_X | LQ | SL
    
    # Main loop
    while LQ or SL:
        B = get_buyers()
        if not B:
            break
            
        PvP = cost / len(B)  # per-voter price
        
        # Check condition in Line 7: leximax payment < (PvP, p)
        # i.e., the solvent voter with smallest leximax can't afford PvP
        if j < len(leximax_list):
            wj, cj = leximax_list[j]
            # cj <_lex (PvP, p) means voter wj should be removed from SL
            if leximax_lt(cj, (PvP, project_id)):
                SL.discard(wj)
                j += 1
                continue
        
        # Process leftover budgets list
        if i < len(leftover_list):
            vi, ri = leftover_list[i]
            
            if vi not in LQ:
                # Already removed, skip
                i += 1
                continue
            
            # Get leximax payment for vi
            ci = outcome.leximax_payment(vi)
            
            # Check if vi qualifies as solvent: ci >_lex (PvP, p)
            if leximax_gt(ci, (PvP, project_id)):
                # Move vi from LQ to SL
                LQ.discard(vi)
                SL.add(vi)
                i += 1
                continue
            
            # vi is not solvent, compute required increase
            # d = min(d, PvP - ri)
            required = PvP - ri
            if required > 0:
                if d is None or required < d:
                    d = required
            
            # Remove vi from LQ
            LQ.discard(vi)
            i += 1
            continue
        
        # If we've exhausted leftover_list but still have SL voters,
        # we need to check if they should be removed
        if j < len(leximax_list):
            wj, cj = leximax_list[j]
            if leximax_lt(cj, (PvP, project_id)):
                SL.discard(wj)
                j += 1
                continue
        
        # No more progress possible
        break
    
    return d
