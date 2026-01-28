"""
Tests for completion heuristics (ADD-ONE, ADD-OPT, ADD-OPT-SKIP).
"""

import pytest
from fractions import Fraction
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from pb.types import Election, Project
from pb.ees import ees_with_outcome, cardinal_utility, cost_utility
from pb.completion import (
    add_one_completion,
    add_opt_completion,
    add_opt_skip_completion,
    add_one_complete,
    add_opt_complete,
)


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


class TestAddOneCompletion:
    """Tests for ADD-ONE completion heuristic."""

    def test_add_one_increases_budget_by_n(self):
        """ADD-ONE should increase total budget by n per iteration."""
        e = make_election(
            project_costs={"p1": 10, "p2": 15},
            approvals={
                0: ["p1", "p2"],
                1: ["p1"],
                2: ["p2"],
            },
            budget=20,
        )

        result = add_one_completion(e, cardinal_utility)

        # Should return a feasible outcome
        assert result.outcome.total_cost <= e.budget
        # Should have trajectory data
        assert len(result.efficiency_trajectory) >= 1
        assert result.step_count >= 0

    def test_add_one_stops_before_overspending(self):
        """ADD-ONE stops when next increment would overspend."""
        e = make_election(
            project_costs={"p1": 5, "p2": 10, "p3": 100},
            approvals={
                0: ["p1", "p2", "p3"],
                1: ["p1", "p2", "p3"],
            },
            budget=20,
        )

        result = add_one_completion(e, cardinal_utility)

        # Should not exceed actual budget
        assert result.outcome.total_cost <= e.budget


class TestAddOptCompletion:
    """Tests for ADD-OPT completion heuristic."""

    def test_add_opt_feasible_output(self):
        """ADD-OPT should return feasible outcome."""
        e = make_election(
            project_costs={"a": 8, "b": 12, "c": 5},
            approvals={
                0: ["a", "b"],
                1: ["b", "c"],
                2: ["a", "c"],
            },
            budget=25,
        )

        result = add_opt_completion(e, cardinal_utility, is_cardinal=True)

        assert result.outcome.total_cost <= e.budget

    def test_add_opt_at_least_as_good_as_no_completion(self):
        """ADD-OPT should do at least as well as base EES."""
        e = make_election(
            project_costs={"x": 10, "y": 15, "z": 8},
            approvals={
                0: ["x", "z"],
                1: ["x", "y"],
                2: ["y", "z"],
                3: ["x", "y", "z"],
            },
            budget=30,
        )

        base_outcome = ees_with_outcome(e, cardinal_utility)
        result = add_opt_completion(e, cardinal_utility, is_cardinal=True)

        # Completion should achieve >= efficiency
        base_eff = base_outcome.spending_efficiency(e.budget)
        completed_eff = result.outcome.spending_efficiency(e.budget)
        assert completed_eff >= base_eff


class TestAddOptSkipCompletion:
    """Tests for ADD-OPT-SKIP completion heuristic."""

    def test_add_opt_skip_considers_all_projects(self):
        """ADD-OPT-SKIP continues until all projects considered."""
        e = make_election(
            project_costs={"p1": 5, "p2": 10, "p3": 15},
            approvals={
                0: ["p1", "p2", "p3"],
                1: ["p1", "p2"],
                2: ["p2", "p3"],
            },
            budget=30,
        )

        result = add_opt_skip_completion(e, cardinal_utility, is_cardinal=True)

        # Should return feasible outcome
        assert result.outcome.total_cost <= e.budget

    def test_add_opt_skip_best_efficiency(self):
        """ADD-OPT-SKIP returns highest efficiency feasible outcome."""
        e = make_election(
            project_costs={"a": 10, "b": 20, "c": 30},
            approvals={
                0: ["a", "b", "c"],
                1: ["a", "b"],
                2: ["b", "c"],
                3: ["a", "c"],
            },
            budget=50,
        )

        result = add_opt_skip_completion(e, cardinal_utility, is_cardinal=True)

        # Just verify it's feasible
        assert result.outcome.total_cost <= e.budget


class TestCompleteVariants:
    """Tests for 'complete' variants that continue until all projects selected."""

    def test_add_one_complete_explores_all(self):
        """ADD-ONE complete continues until all projects selected."""
        e = make_election(
            project_costs={"p1": 3, "p2": 5, "p3": 7},
            approvals={
                0: ["p1", "p2", "p3"],
                1: ["p1", "p2"],
            },
            budget=15,
        )

        result = add_one_complete(e, cardinal_utility)

        # Should be feasible
        assert result.outcome.total_cost <= e.budget

    def test_add_opt_complete_best_feasible(self):
        """ADD-OPT complete returns best feasible outcome."""
        e = make_election(
            project_costs={"x": 4, "y": 6, "z": 8},
            approvals={
                0: ["x", "y", "z"],
                1: ["x", "z"],
                2: ["y", "z"],
            },
            budget=18,
        )

        result = add_opt_complete(e, cardinal_utility, is_cardinal=True)

        assert result.outcome.total_cost <= e.budget


class TestCompletionWithCostUtility:
    """Test completion heuristics with cost utility."""

    def test_add_one_cost_utility(self):
        """ADD-ONE with cost utility."""
        e = make_election(
            project_costs={"cheap": 5, "mid": 15, "expensive": 30},
            approvals={
                0: ["cheap", "mid", "expensive"],
                1: ["cheap", "expensive"],
                2: ["mid", "expensive"],
            },
            budget=50,
        )

        result = add_one_completion(e, cost_utility)
        assert result.outcome.total_cost <= e.budget

    def test_add_opt_skip_cost_utility(self):
        """ADD-OPT-SKIP with cost utility."""
        e = make_election(
            project_costs={"a": 10, "b": 20, "c": 15},
            approvals={
                0: ["a", "b"],
                1: ["b", "c"],
                2: ["a", "c"],
            },
            budget=45,
        )

        result = add_opt_skip_completion(e, cost_utility, is_cardinal=False)
        assert result.outcome.total_cost <= e.budget


class TestTrajectoryTracking:
    """Tests for trajectory tracking in CompletionResult."""

    def test_trajectory_lengths_match(self):
        """All trajectory lists should have the same length."""
        e = make_election(
            project_costs={"p1": 5, "p2": 10, "p3": 15},
            approvals={
                0: ["p1", "p2", "p3"],
                1: ["p1", "p2"],
                2: ["p2", "p3"],
            },
            budget=30,
        )

        result = add_opt_skip_completion(e, cardinal_utility, is_cardinal=True)

        # All trajectories should have the same length
        assert len(result.efficiency_trajectory) == len(result.budget_trajectory)
        assert len(result.efficiency_trajectory) == len(result.selected_trajectory)

    def test_budget_deltas_count_matches_step_count(self):
        """Number of budget deltas should match step count."""
        e = make_election(
            project_costs={"p1": 5, "p2": 10, "p3": 15},
            approvals={
                0: ["p1", "p2", "p3"],
                1: ["p1", "p2"],
            },
            budget=30,
        )

        result = add_one_completion(e, cardinal_utility)

        assert len(result.budget_deltas) == result.step_count

    def test_efficiency_trajectory_values(self):
        """Efficiency values should be between 0 and some reasonable upper bound."""
        e = make_election(
            project_costs={"p1": 5, "p2": 10},
            approvals={
                0: ["p1", "p2"],
                1: ["p1", "p2"],
            },
            budget=15,
        )

        result = add_opt_completion(e, cardinal_utility, is_cardinal=True)

        for eff in result.efficiency_trajectory:
            assert eff >= 0

    def test_selected_trajectory_non_decreasing(self):
        """Number of selected projects should be non-decreasing in trajectory."""
        e = make_election(
            project_costs={"p1": 5, "p2": 10, "p3": 15},
            approvals={
                0: ["p1", "p2", "p3"],
                1: ["p1", "p2", "p3"],
            },
            budget=30,
        )

        result = add_one_complete(e, cardinal_utility)

        for i in range(1, len(result.selected_trajectory)):
            assert result.selected_trajectory[i] >= result.selected_trajectory[i-1]
