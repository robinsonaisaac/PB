"""
Tests for Exact Equal Shares (EES) - Algorithm 1

Tests EES core functionality and invariants.
"""

import pytest
from fractions import Fraction
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from pb.types import Election, Project, EESOutcome
from pb.ees import ees, ees_with_outcome, cardinal_utility, cost_utility


def make_election(
    project_costs: dict,  # {id: cost}
    approvals: dict,  # {voter_id: [project_ids]}
    budget: int,
) -> Election:
    """Helper to create Election from simple dicts."""
    projects = {
        pid: Project(id=pid, cost=Fraction(cost))
        for pid, cost in project_costs.items()
    }
    voters = list(approvals.keys())
    approval_sets = {v: set(approvals[v]) for v in voters}
    return Election(
        projects=projects,
        voters=voters,
        approvals=approval_sets,
        budget=Fraction(budget),
    )


class TestEESBasic:
    """Basic EES functionality tests."""
    
    def test_empty_election(self):
        """EES on election with no projects."""
        e = Election(
            projects={},
            voters=[0, 1],
            approvals={0: set(), 1: set()},
            budget=Fraction(100),
        )
        outcome = ees_with_outcome(e)
        assert outcome.selected == set()
        assert outcome.total_cost == 0
    
    def test_single_project_funded(self):
        """Single project that can be funded."""
        e = make_election(
            project_costs={"p1": 10},
            approvals={0: ["p1"], 1: ["p1"]},
            budget=10,
        )
        outcome = ees_with_outcome(e)
        assert outcome.selected == {"p1"}
        assert outcome.total_cost == 10
        # Each voter should pay 5
        assert outcome.payment(0, "p1") == Fraction(5)
        assert outcome.payment(1, "p1") == Fraction(5)
    
    def test_single_project_too_expensive(self):
        """Single project that cannot be funded."""
        e = make_election(
            project_costs={"p1": 100},
            approvals={0: ["p1"], 1: ["p1"]},
            budget=10,  # Only 5 per voter
        )
        outcome = ees_with_outcome(e)
        # Project costs 100, but voters only have 10 total
        assert outcome.selected == set()
    
    def test_tie_breaking_by_project_id(self):
        """When BpB is equal, larger project id wins."""
        e = make_election(
            project_costs={"a": 10, "b": 10},
            approvals={0: ["a", "b"], 1: ["a", "b"]},
            budget=20,
        )
        outcome = ees_with_outcome(e)
        # Both have same BpB, "b" > "a" so "b" selected first
        assert "b" in outcome.selected
        # Check selection order
        assert outcome.selection_order[0][0] == "b"


class TestEESInvariants:
    """Test EES output invariants."""
    
    def test_equal_sharing_invariant(self):
        """All payers on a project pay the same amount."""
        e = make_election(
            project_costs={"p1": 12, "p2": 8},
            approvals={
                0: ["p1", "p2"],
                1: ["p1", "p2"],
                2: ["p1"],
                3: ["p2"],
            },
            budget=100,
        )
        outcome = ees_with_outcome(e)
        
        for p_id in outcome.selected:
            payers = outcome.project_payers(p_id)
            if payers:
                payments = [outcome.payment(v, p_id) for v in payers]
                # All payments should be equal
                assert all(p == payments[0] for p in payments)
    
    def test_payments_sum_to_cost(self):
        """Payments for a project sum to its cost."""
        e = make_election(
            project_costs={"p1": 15, "p2": 10, "p3": 5},
            approvals={
                0: ["p1", "p2"],
                1: ["p1", "p3"],
                2: ["p2", "p3"],
            },
            budget=30,
        )
        outcome = ees_with_outcome(e)
        
        for p_id in outcome.selected:
            project = e.projects[p_id]
            total_payment = sum(
                outcome.payment(v, p_id)
                for v in e.voters
            )
            assert total_payment == project.cost
    
    def test_voter_budget_not_exceeded(self):
        """No voter pays more than their initial budget."""
        e = make_election(
            project_costs={"p1": 10, "p2": 10, "p3": 10},
            approvals={
                0: ["p1", "p2", "p3"],
                1: ["p1", "p2"],
                2: ["p2", "p3"],
            },
            budget=30,  # 10 per voter
        )
        outcome = ees_with_outcome(e)
        
        initial_budget = e.budget / e.n
        for v in e.voters:
            total_paid = sum(
                outcome.payment(v, p_id)
                for p_id in e.projects
            )
            assert total_paid <= initial_budget
    
    def test_leftover_budget_nonnegative(self):
        """All leftover budgets are non-negative."""
        e = make_election(
            project_costs={"p1": 6, "p2": 8},
            approvals={
                0: ["p1"],
                1: ["p1", "p2"],
                2: ["p2"],
            },
            budget=30,
        )
        outcome = ees_with_outcome(e)
        
        for v in e.voters:
            assert outcome.leftover_budgets[v] >= 0


class TestEESCostUtility:
    """Test EES with cost utility (u(p) = cost(p))."""
    
    def test_cost_utility_basic(self):
        """Cost utility changes bang-per-buck calculation."""
        # With cardinal utility: BpB = |payers| / cost
        # With cost utility: BpB = cost * |payers| / cost = |payers|
        e = make_election(
            project_costs={"cheap": 10, "expensive": 100},
            approvals={
                0: ["cheap", "expensive"],
                1: ["cheap", "expensive"],
            },
            budget=200,
        )
        
        # Cardinal: cheap has BpB = 2/10 = 0.2, expensive has BpB = 2/100 = 0.02
        # -> cheap selected first
        cardinal_outcome = ees_with_outcome(e, cardinal_utility)
        assert cardinal_outcome.selection_order[0][0] == "cheap"
        
        # Cost: both have BpB = 2
        # Tie-break by id: "expensive" > "cheap"
        cost_outcome = ees_with_outcome(e, cost_utility)
        assert cost_outcome.selection_order[0][0] == "expensive"


class TestEESPaperExample:
    """
    Test based on Example 4.3 from the paper.
    
    Instance:
    - 5 voters: v1, v2, v3, v4, v5
    - 3 projects: p1 (cost 2), p2 (cost 3.2), p3 (cost 6)
    - Budget b = 10
    - Approvals:
      - N_{p1} = {v1, v2}
      - N_{p2} = {v3, v4}
      - N_{p3} = {v2, v3, v4, v5}
    
    EES should select W = {p1, p2}.
    """
    
    def test_example_4_3_ees_outcome(self):
        """Verify EES outcome matches paper's Example 4.3."""
        e = make_election(
            project_costs={
                "p1": 2,
                "p2": Fraction("3.2"),  # 16/5
                "p3": 6,
            },
            approvals={
                0: ["p1"],          # v1
                1: ["p1", "p3"],    # v2
                2: ["p2", "p3"],    # v3
                3: ["p2", "p3"],    # v4
                4: ["p3"],          # v5
            },
            budget=10,
        )
        
        outcome = ees_with_outcome(e, cardinal_utility)
        
        # Should select p1 and p2
        assert outcome.selected == {"p1", "p2"}
        
        # Verify payments
        # p1: cost 2, 2 supporters (v1, v2) -> each pays 1
        assert outcome.payment(0, "p1") == Fraction(1)
        assert outcome.payment(1, "p1") == Fraction(1)
        
        # p2: cost 3.2, 2 supporters (v3, v4) -> each pays 1.6
        assert outcome.payment(2, "p2") == Fraction("1.6")
        assert outcome.payment(3, "p2") == Fraction("1.6")


class TestEESDeterminism:
    """Test that EES is deterministic."""
    
    def test_deterministic_output(self):
        """Running EES multiple times gives same result."""
        e = make_election(
            project_costs={"a": 5, "b": 5, "c": 5, "d": 5},
            approvals={
                0: ["a", "b"],
                1: ["b", "c"],
                2: ["c", "d"],
                3: ["d", "a"],
            },
            budget=20,
        )
        
        outcomes = [ees_with_outcome(e) for _ in range(5)]
        
        # All should have same selected set
        for o in outcomes[1:]:
            assert o.selected == outcomes[0].selected
            assert o.selection_order == outcomes[0].selection_order

