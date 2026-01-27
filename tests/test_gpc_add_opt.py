"""
Tests for GREEDYPROJECTCHANGE and ADD-OPT algorithms.

Tests Algorithm 2 (GPC cardinal), Algorithm 3 (ADD-OPT cardinal),
Algorithm 4 (GPC uniform), and Algorithm 5 (ADD-OPT uniform).
"""

import pytest
from fractions import Fraction
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from scalable_proportional_pb.types import Election, Project, EESOutcome
from scalable_proportional_pb.ees import ees_with_outcome, cardinal_utility, cost_utility
from scalable_proportional_pb.gpc_cardinal import greedy_project_change_cardinal
from scalable_proportional_pb.add_opt_cardinal import add_opt_cardinal
from scalable_proportional_pb.gpc_uniform import greedy_project_change_uniform, compute_L_lists
from scalable_proportional_pb.add_opt_uniform import add_opt_uniform


def make_election(
    project_costs: dict,
    approvals: dict,
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


class TestGPCCardinalExample43:
    """
    Test GREEDYPROJECTCHANGE on Example 4.3 from the paper.
    
    Instance:
    - 5 voters, 3 projects: p1 (cost 2), p2 (cost 3.2), p3 (cost 6)
    - Budget b = 10
    - EES selects W = {p1, p2}
    
    Running GPC on p3:
    - N_{p3} = {v2, v3, v4, v5}
    - PvP = 6/4 = 1.5
    - Paper says algorithm returns d = 0.5
    """
    
    def test_gpc_cardinal_returns_0_5(self):
        """GPC for p3 should return d = 0.5."""
        e = make_election(
            project_costs={
                "p1": 2,
                "p2": Fraction("3.2"),
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
        assert outcome.selected == {"p1", "p2"}
        
        d = greedy_project_change_cardinal(e, outcome, "p3")
        
        # Paper says d = 0.5
        assert d == Fraction("0.5")


class TestGPCCardinalBasic:
    """Basic tests for GREEDYPROJECTCHANGE cardinal."""
    
    def test_project_already_selected(self):
        """GPC on already-selected project."""
        e = make_election(
            project_costs={"p1": 10},
            approvals={0: ["p1"], 1: ["p1"]},
            budget=10,
        )
        outcome = ees_with_outcome(e)
        assert "p1" in outcome.selected
        
        # No supporters left who aren't paying -> should return None (inf)
        d = greedy_project_change_cardinal(e, outcome, "p1")
        assert d is None
    
    def test_no_supporters(self):
        """GPC on project with no supporters."""
        e = make_election(
            project_costs={"p1": 10, "p2": 5},
            approvals={0: ["p1"], 1: ["p1"]},  # No one approves p2
            budget=20,
        )
        outcome = ees_with_outcome(e)
        
        d = greedy_project_change_cardinal(e, outcome, "p2")
        assert d is None  # Infinity


class TestAddOptCardinal:
    """Tests for ADD-OPT cardinal (Algorithm 3)."""
    
    def test_add_opt_minimum_over_projects(self):
        """ADD-OPT returns minimum d over all projects."""
        e = make_election(
            project_costs={
                "p1": 2,
                "p2": Fraction("3.2"),
                "p3": 6,
            },
            approvals={
                0: ["p1"],
                1: ["p1", "p3"],
                2: ["p2", "p3"],
                3: ["p2", "p3"],
                4: ["p3"],
            },
            budget=10,
        )
        
        outcome = ees_with_outcome(e, cardinal_utility)
        d = add_opt_cardinal(e, outcome)
        
        # Should be minimum of GPC over all projects
        # From Example 4.3, GPC(p3) = 0.5
        assert d <= Fraction("0.5")
    
    def test_add_opt_infinity_when_stable(self):
        """ADD-OPT returns None (infinity) when all projects selected."""
        e = make_election(
            project_costs={"p1": 5, "p2": 5},
            approvals={0: ["p1", "p2"], 1: ["p1", "p2"]},
            budget=100,  # Plenty of budget
        )
        
        outcome = ees_with_outcome(e)
        # Both projects should be selected
        assert outcome.selected == {"p1", "p2"}
        
        d = add_opt_cardinal(e, outcome)
        assert d is None  # Infinity


class TestBruteForceCardinal:
    """Brute-force verification of ADD-OPT cardinal on tiny instances."""
    
    def test_brute_force_small_instance(self):
        """
        Verify ADD-OPT by brute-force searching for smallest d
        that changes the EES outcome.
        """
        e = make_election(
            project_costs={"a": 4, "b": 6},
            approvals={
                0: ["a"],
                1: ["a", "b"],
                2: ["b"],
            },
            budget=10,
        )
        
        outcome = ees_with_outcome(e)
        add_opt_d = add_opt_cardinal(e, outcome)
        
        if add_opt_d is None:
            # All projects selected or stable, nothing to verify
            assert outcome.selected == {"a", "b"}
            return
        
        n = e.n
        
        # Brute-force: try increments of 0.01 to find where outcome changes
        brute_d = None
        for i in range(1, 10000):
            test_d = Fraction(i, 100)
            new_budget = e.budget + n * test_d
            e_new = e.with_budget(new_budget)
            new_outcome = ees_with_outcome(e_new)
            
            if new_outcome.selected != outcome.selected:
                brute_d = test_d
                break
        
        if brute_d is not None:
            # ADD-OPT should give d <= brute_d (may be more precise)
            assert add_opt_d <= brute_d
            # And the outcome should actually change at budget b + n * add_opt_d
            e_check = e.with_budget(e.budget + n * add_opt_d)
            check_outcome = ees_with_outcome(e_check)
            # Note: might select same set but with different payers
            # Just verify something changed
            assert (
                check_outcome.selected != outcome.selected or
                check_outcome.payments != outcome.payments
            )


class TestRemark1Scenario:
    """
    Test the scenario from Remark 1 in the paper.
    
    This tests that GPC for p4 returns d = 51 (full cost),
    but there exists p2 with smaller d = 1 that would allow p4
    to be selected at a later step.
    
    Instance:
    - 4 projects: p1 (cost 2), p2 (cost 98), p3 (cost 100), p4 (cost 51)
    - 3 voters
    - Budget b = 150
    - A1 = {p1, p2}, A2 = {p2, p3}, A3 = {p3, p4}
    - EES selects {p1, p3}
    """
    
    def test_remark1_ees_outcome(self):
        """Verify EES selects {p1, p3}."""
        e = make_election(
            project_costs={
                "p1": 2,
                "p2": 98,
                "p3": 100,
                "p4": 51,
            },
            approvals={
                0: ["p1", "p2"],  # A1
                1: ["p2", "p3"],  # A2
                2: ["p3", "p4"],  # A3
            },
            budget=150,
        )
        
        outcome = ees_with_outcome(e, cardinal_utility)
        assert outcome.selected == {"p1", "p3"}
    
    def test_remark1_gpc_p4(self):
        """GPC for p4 returns cost(p4) = 51."""
        e = make_election(
            project_costs={
                "p1": 2,
                "p2": 98,
                "p3": 100,
                "p4": 51,
            },
            approvals={
                0: ["p1", "p2"],
                1: ["p2", "p3"],
                2: ["p3", "p4"],
            },
            budget=150,
        )
        
        outcome = ees_with_outcome(e, cardinal_utility)
        d_p4 = greedy_project_change_cardinal(e, outcome, "p4")
        
        # Paper says d = 51 for p4
        assert d_p4 == Fraction(51)
    
    def test_remark1_add_opt_finds_smaller(self):
        """ADD-OPT finds d < 51 via p2."""
        e = make_election(
            project_costs={
                "p1": 2,
                "p2": 98,
                "p3": 100,
                "p4": 51,
            },
            approvals={
                0: ["p1", "p2"],
                1: ["p2", "p3"],
                2: ["p3", "p4"],
            },
            budget=150,
        )
        
        outcome = ees_with_outcome(e, cardinal_utility)
        d = add_opt_cardinal(e, outcome)
        
        # Paper says d' = 1 certifies instability via p2
        # ADD-OPT should return at most 1
        assert d <= Fraction(1)


class TestUniformUtility:
    """Tests for uniform utility (cost utility) algorithms."""
    
    def test_add_opt_uniform_basic(self):
        """Basic test for ADD-OPT with cost utility."""
        e = make_election(
            project_costs={"a": 10, "b": 20, "c": 30},
            approvals={
                0: ["a", "c"],
                1: ["a", "b"],
                2: ["b", "c"],
            },
            budget=60,
        )
        
        outcome = ees_with_outcome(e, cost_utility)
        
        if len(outcome.selected) < 3:
            d = add_opt_uniform(e, outcome, cost_utility)
            # Should return a valid increment or infinity
            assert d >= 0

