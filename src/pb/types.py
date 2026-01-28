"""
Core data types for participatory budgeting.

Tie-breaking order: lexicographic by project id (string comparison).
"""

from dataclasses import dataclass, field
from fractions import Fraction
from typing import Dict, FrozenSet, List, Set, Tuple, Optional
from collections import OrderedDict


@dataclass(frozen=True, order=True)
class Project:
    """
    A project in a participatory budgeting election.
    
    Ordering is lexicographic by id (for deterministic tie-breaking).
    """
    id: str
    cost: Fraction  # Use exact arithmetic
    
    def __hash__(self):
        return hash(self.id)
    
    def __eq__(self, other):
        if not isinstance(other, Project):
            return False
        return self.id == other.id


@dataclass
class Election:
    """
    A participatory budgeting election E(b) = (N, P, {A_i}, cost, b).
    
    Attributes:
        projects: dict mapping project id -> Project
        voters: list of voter ids (0-indexed integers for simplicity)
        approvals: dict mapping voter_id -> set of project ids they approve
        budget: total budget b
    """
    projects: Dict[str, Project]
    voters: List[int]
    approvals: Dict[int, Set[str]]  # voter_id -> set of approved project ids
    budget: Fraction
    
    @property
    def n(self) -> int:
        """Number of voters."""
        return len(self.voters)
    
    @property
    def m(self) -> int:
        """Number of projects."""
        return len(self.projects)
    
    def project_supporters(self, project_id: str) -> Set[int]:
        """Return set of voters who approve the given project."""
        return {v for v in self.voters if project_id in self.approvals.get(v, set())}
    
    def with_budget(self, new_budget: Fraction) -> "Election":
        """Return a copy of this election with a different budget."""
        return Election(
            projects=self.projects,
            voters=self.voters,
            approvals=self.approvals,
            budget=new_budget,
        )


@dataclass
class EESOutcome:
    """
    The outcome of running EES on an election.
    
    (W, X) where:
    - W is the set of selected projects
    - X is the payment matrix: X[voter_id, project_id] = payment amount
    
    Also stores auxiliary info for ADD-OPT algorithms:
    - leftover_budgets: voter_id -> remaining budget r_i
    - selection_order: list of (project_id, bang_per_buck) in selection order
    """
    selected: Set[str]  # project ids
    payments: Dict[Tuple[int, str], Fraction]  # (voter_id, project_id) -> payment
    leftover_budgets: Dict[int, Fraction]  # voter_id -> leftover budget
    selection_order: List[Tuple[str, Fraction]]  # (project_id, bpb) in order selected
    total_cost: Fraction
    
    def payment(self, voter_id: int, project_id: str) -> Fraction:
        """Get payment from voter to project (0 if not paying)."""
        return self.payments.get((voter_id, project_id), Fraction(0))
    
    def project_payers(self, project_id: str) -> Set[int]:
        """Return set of voters paying for the given project."""
        return {v for (v, p), amt in self.payments.items() if p == project_id and amt > 0}
    
    def leximax_payment(self, voter_id: int) -> Tuple[Fraction, Optional[str]]:
        """
        Return the leximax payment (x_i, p_i) for voter i.
        
        x_i = max payment made by voter i to any project
        p_i = lexicographically largest project receiving x_i from voter i
        
        Returns (0, None) if voter makes no payments.
        """
        max_payment = Fraction(0)
        max_project = None
        
        for (v, p), amt in self.payments.items():
            if v == voter_id and amt > 0:
                if amt > max_payment or (amt == max_payment and (max_project is None or p > max_project)):
                    max_payment = amt
                    max_project = p
        
        return (max_payment, max_project)
    
    def spending_efficiency(self, actual_budget: Fraction) -> Fraction:
        """Return the spending efficiency: total_cost / actual_budget."""
        if actual_budget == 0:
            return Fraction(0)
        return self.total_cost / actual_budget


@dataclass
class CompletionResult:
    """
    Result of running a completion heuristic.

    Tracks the full trajectory of the algorithm, not just the final outcome.

    Attributes:
        outcome: The final/best EESOutcome
        step_count: Number of budget increase iterations
        budget_deltas: List of budget increase amounts (d values) at each step
        efficiency_trajectory: Efficiency at each step (including initial)
        budget_trajectory: Budget level at each step (including initial)
        selected_trajectory: Number of selected projects at each step
    """
    outcome: EESOutcome
    step_count: int
    budget_deltas: List[Fraction]
    efficiency_trajectory: List[Fraction]
    budget_trajectory: List[Fraction]
    selected_trajectory: List[int]

    @property
    def highest_efficiency(self) -> Fraction:
        """Return the highest efficiency achieved during the trajectory."""
        if not self.efficiency_trajectory:
            return Fraction(0)
        return max(self.efficiency_trajectory)

    @property
    def final_efficiency(self) -> Fraction:
        """Return the final efficiency."""
        if not self.efficiency_trajectory:
            return Fraction(0)
        return self.efficiency_trajectory[-1]


def leximax_lt(c1: Tuple[Fraction, Optional[str]], c2: Tuple[Fraction, Optional[str]]) -> bool:
    """
    Compare two leximax payments: c1 <_lex c2.
    
    (x, p) <_lex (x', p') iff x < x' or (x == x' and p >_C p')
    where >_C is the tie-breaking order (lexicographic by project id).
    
    Note: In leximax preferences for stability, a "smaller" value is "better/preferred".
    Since we tie-break by selecting larger IDs (Better), a larger ID must appear
    "smaller" in the leximax order to be preferred.
    """
    x1, p1 = c1
    x2, p2 = c2
    
    if x1 < x2:
        return True
    if x1 > x2:
        return False
    # x1 == x2
    if p1 is None and p2 is None:
        return False
    if p1 is None:
        return True  # None (no payment) is < any payment? 
        # Wait, usually (0, None) is the smallest possible payment.
        # But if amounts are equal, p1=None implies x1=0.
    if p2 is None:
        return False
    
    # Invert comparison: Better project (larger ID) is "smaller" in leximax order
    return p1 > p2


def leximax_gt(c1: Tuple[Fraction, Optional[str]], c2: Tuple[Fraction, Optional[str]]) -> bool:
    """c1 >_lex c2"""
    return leximax_lt(c2, c1)


def leximax_eq(c1: Tuple[Fraction, Optional[str]], c2: Tuple[Fraction, Optional[str]]) -> bool:
    """c1 ==_lex c2"""
    return c1 == c2

