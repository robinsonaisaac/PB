"""
Completion Heuristics for EES

From "Streamlining Equal Shares" (arXiv:2502.11797), Section 6.2.

Implements:
- ADD-ONE: Increase budget by n (i.e., +1 per voter) until overspending
- ADD-OPT: Use optimal budget increment from ADD-OPT algorithm
- ADD-OPT-SKIP: Like ADD-OPT but only consider unselected projects

Each has a "complete" variant that continues until all projects are selected,
then returns the feasible outcome with highest spending efficiency.

All functions return CompletionResult with full trajectory tracking:
- step_count: number of iterations
- budget_deltas: list of budget increases at each step
- efficiency_trajectory: efficiency at each step
- budget_trajectory: budget level at each step
- selected_trajectory: number of selected projects at each step
"""

from fractions import Fraction
from typing import Callable, List, Optional, Tuple

from .types import Election, EESOutcome, Project, CompletionResult
from .ees import ees_with_outcome
from .add_opt_cardinal import add_opt_cardinal
from .add_opt_uniform import add_opt_uniform
from .gpc_cardinal import greedy_project_change_cardinal
from .gpc_uniform import greedy_project_change_uniform, compute_L_lists


def add_one_completion(
    election: Election,
    utility: Callable[[Project], Fraction],
) -> CompletionResult:
    """
    ADD-ONE completion: increase budget by n per iteration until overspending.

    Returns CompletionResult with the last feasible outcome before overspending
    and the full trajectory.
    """
    actual_budget = election.budget
    n = election.n

    current_budget = election.budget
    best_outcome: Optional[EESOutcome] = None

    # Trajectory tracking
    step_count = 0
    budget_deltas: List[Fraction] = []
    efficiency_trajectory: List[Fraction] = []
    budget_trajectory: List[Fraction] = []
    selected_trajectory: List[int] = []

    while True:
        e = election.with_budget(current_budget)
        outcome = ees_with_outcome(e, utility)

        # Record trajectory point
        eff = outcome.spending_efficiency(actual_budget)
        efficiency_trajectory.append(eff)
        budget_trajectory.append(current_budget)
        selected_trajectory.append(len(outcome.selected))

        if outcome.total_cost > actual_budget:
            # Overspending, return previous outcome
            break

        best_outcome = outcome

        if len(outcome.selected) == election.m:
            # All projects selected
            break

        # Increase budget by n (i.e., +1 per voter)
        d = Fraction(1)
        budget_deltas.append(d)
        step_count += 1
        current_budget += n * d

    if best_outcome is None:
        # Edge case: even initial budget causes overspending
        best_outcome = ees_with_outcome(election, utility)

    return CompletionResult(
        outcome=best_outcome,
        step_count=step_count,
        budget_deltas=budget_deltas,
        efficiency_trajectory=efficiency_trajectory,
        budget_trajectory=budget_trajectory,
        selected_trajectory=selected_trajectory,
    )


def add_opt_completion(
    election: Election,
    utility: Callable[[Project], Fraction],
    is_cardinal: bool = True,
) -> CompletionResult:
    """
    ADD-OPT completion: use optimal budget increment until overspending.

    Returns CompletionResult with the last feasible outcome before overspending
    and the full trajectory.
    """
    actual_budget = election.budget
    n = election.n

    current_budget = election.budget
    best_outcome: Optional[EESOutcome] = None

    # Trajectory tracking
    step_count = 0
    budget_deltas: List[Fraction] = []
    efficiency_trajectory: List[Fraction] = []
    budget_trajectory: List[Fraction] = []
    selected_trajectory: List[int] = []

    while True:
        e = election.with_budget(current_budget)
        outcome = ees_with_outcome(e, utility)

        # Record trajectory point
        eff = outcome.spending_efficiency(actual_budget)
        efficiency_trajectory.append(eff)
        budget_trajectory.append(current_budget)
        selected_trajectory.append(len(outcome.selected))

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

        budget_deltas.append(d)
        step_count += 1
        current_budget += n * d

    if best_outcome is None:
        best_outcome = ees_with_outcome(election, utility)

    return CompletionResult(
        outcome=best_outcome,
        step_count=step_count,
        budget_deltas=budget_deltas,
        efficiency_trajectory=efficiency_trajectory,
        budget_trajectory=budget_trajectory,
        selected_trajectory=selected_trajectory,
    )


def add_opt_skip_completion(
    election: Election,
    utility: Callable[[Project], Fraction],
    is_cardinal: bool = True,
) -> CompletionResult:
    """
    ADD-OPT-SKIP completion: like ADD-OPT but only consider unselected projects.

    This is more efficient and continues until all projects are considered.
    Returns CompletionResult with the feasible outcome with highest spending
    efficiency and the full trajectory.
    """
    actual_budget = election.budget
    n = election.n

    current_budget = election.budget
    all_outcomes: List[Tuple[Fraction, EESOutcome]] = []  # (efficiency, outcome)

    # Trajectory tracking
    step_count = 0
    budget_deltas: List[Fraction] = []
    efficiency_trajectory: List[Fraction] = []
    budget_trajectory: List[Fraction] = []
    selected_trajectory: List[int] = []

    while True:
        e = election.with_budget(current_budget)
        outcome = ees_with_outcome(e, utility)

        # Record trajectory point
        eff = outcome.spending_efficiency(actual_budget)
        efficiency_trajectory.append(eff)
        budget_trajectory.append(current_budget)
        selected_trajectory.append(len(outcome.selected))

        # Record if feasible
        if outcome.total_cost <= actual_budget:
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

        budget_deltas.append(d)
        step_count += 1
        current_budget += n * d

    if not all_outcomes:
        best_outcome = ees_with_outcome(election, utility)
    else:
        # Return outcome with highest efficiency
        all_outcomes.sort(key=lambda x: x[0], reverse=True)
        best_outcome = all_outcomes[0][1]

    return CompletionResult(
        outcome=best_outcome,
        step_count=step_count,
        budget_deltas=budget_deltas,
        efficiency_trajectory=efficiency_trajectory,
        budget_trajectory=budget_trajectory,
        selected_trajectory=selected_trajectory,
    )


def add_one_complete(
    election: Election,
    utility: Callable[[Project], Fraction],
) -> CompletionResult:
    """
    ADD-ONE (complete): continue until all projects selected,
    then return feasible outcome with highest efficiency.
    """
    actual_budget = election.budget
    n = election.n

    current_budget = election.budget
    all_outcomes: List[Tuple[Fraction, EESOutcome]] = []

    # Trajectory tracking
    step_count = 0
    budget_deltas: List[Fraction] = []
    efficiency_trajectory: List[Fraction] = []
    budget_trajectory: List[Fraction] = []
    selected_trajectory: List[int] = []

    while True:
        e = election.with_budget(current_budget)
        outcome = ees_with_outcome(e, utility)

        # Record trajectory point
        eff = outcome.spending_efficiency(actual_budget)
        efficiency_trajectory.append(eff)
        budget_trajectory.append(current_budget)
        selected_trajectory.append(len(outcome.selected))

        if outcome.total_cost <= actual_budget:
            all_outcomes.append((eff, outcome))

        if len(outcome.selected) == election.m:
            break

        d = Fraction(1)
        budget_deltas.append(d)
        step_count += 1
        current_budget += n * d

    if not all_outcomes:
        best_outcome = ees_with_outcome(election, utility)
    else:
        all_outcomes.sort(key=lambda x: x[0], reverse=True)
        best_outcome = all_outcomes[0][1]

    return CompletionResult(
        outcome=best_outcome,
        step_count=step_count,
        budget_deltas=budget_deltas,
        efficiency_trajectory=efficiency_trajectory,
        budget_trajectory=budget_trajectory,
        selected_trajectory=selected_trajectory,
    )


def add_opt_complete(
    election: Election,
    utility: Callable[[Project], Fraction],
    is_cardinal: bool = True,
) -> CompletionResult:
    """
    ADD-OPT (complete): continue until all projects selected,
    then return feasible outcome with highest efficiency.
    """
    actual_budget = election.budget
    n = election.n

    current_budget = election.budget
    all_outcomes: List[Tuple[Fraction, EESOutcome]] = []

    # Trajectory tracking
    step_count = 0
    budget_deltas: List[Fraction] = []
    efficiency_trajectory: List[Fraction] = []
    budget_trajectory: List[Fraction] = []
    selected_trajectory: List[int] = []

    while True:
        e = election.with_budget(current_budget)
        outcome = ees_with_outcome(e, utility)

        # Record trajectory point
        eff = outcome.spending_efficiency(actual_budget)
        efficiency_trajectory.append(eff)
        budget_trajectory.append(current_budget)
        selected_trajectory.append(len(outcome.selected))

        if outcome.total_cost <= actual_budget:
            all_outcomes.append((eff, outcome))

        if len(outcome.selected) == election.m:
            break

        if is_cardinal:
            d = add_opt_cardinal(e, outcome)
        else:
            d = add_opt_uniform(e, outcome, utility)

        if d is None:  # Infinity
            break

        budget_deltas.append(d)
        step_count += 1
        current_budget += n * d

    if not all_outcomes:
        best_outcome = ees_with_outcome(election, utility)
    else:
        all_outcomes.sort(key=lambda x: x[0], reverse=True)
        best_outcome = all_outcomes[0][1]

    return CompletionResult(
        outcome=best_outcome,
        step_count=step_count,
        budget_deltas=budget_deltas,
        efficiency_trajectory=efficiency_trajectory,
        budget_trajectory=budget_trajectory,
        selected_trajectory=selected_trajectory,
    )


def add_opt_skip_complete(
    election: Election,
    utility: Callable[[Project], Fraction],
    is_cardinal: bool = True,
) -> CompletionResult:
    """
    ADD-OPT-SKIP (complete): same as add_opt_skip_completion.

    The SKIP variant already continues until all projects are considered.
    """
    return add_opt_skip_completion(election, utility, is_cardinal)
