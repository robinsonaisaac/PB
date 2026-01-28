#!/usr/bin/env python3
"""
Unified Participatory Budgeting CLI

A single entry point for running all PB algorithms with any combination of:
- Algorithm: EES (Exact Equal Shares) or MES (Method of Equal Shares / Waterflow)
- Utility: cardinal (approval) or cost (uniform)
- Completion: none, add-one, add-opt, add-opt-skip
- Mode: non-exhaustive (stop on overspend) or exhaustive (continue until all selected)

Usage:
    python run_pb.py <input_file> --algorithm ees --utility cardinal --completion add-opt
    python run_pb.py <input_file> --algorithm mes --utility cost --completion none
    python run_pb.py <input_file> -a ees -u cardinal -c add-opt-skip --exhaustive

Examples:
    # EES with cardinal utilities and ADD-OPT completion (non-exhaustive)
    python run_pb.py instance.pb -a ees -u cardinal -c add-opt

    # MES with cost utilities, no completion
    python run_pb.py instance.pb -a mes -u cost -c none

    # EES with ADD-OPT-SKIP heuristic, exhaustive mode
    python run_pb.py instance.pb -a ees -u cost -c add-opt-skip --exhaustive
"""

import argparse
import json
import pandas as pd
from pathlib import Path
import os
import sys
from dataclasses import dataclass, field
from typing import List, Set, Optional, Any
from fractions import Fraction

# Add src to path for pb
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from pb import (
    parse_pabulib_file,
    ees_with_outcome,
    CompletionResult,
)
from pb.ees import cardinal_utility, cost_utility
from pb.types import Election, EESOutcome
from pb.completion import (
    add_one_completion,
    add_opt_completion,
    add_opt_skip_completion,
    add_one_complete,
    add_opt_complete,
    add_opt_skip_complete,
)

from core.cli import setup_results_dir, save_results


# =============================================================================
# Result Dataclasses
# =============================================================================

@dataclass
class EESResult:
    """Result container for EES algorithms with detailed statistics and trajectories."""
    most_efficient_project_set: Set[str]
    highest_efficiency_attained: float
    final_project_set: Set[str]
    final_efficiency: float
    budget_increase_count: int
    budget_increase_list: List[float] = field(default_factory=list)
    efficiency_trajectory: List[float] = field(default_factory=list)
    budget_trajectory: List[float] = field(default_factory=list)
    selected_trajectory: List[int] = field(default_factory=list)
    monotonic_violation: int = 0  # Only tracked in exhaustive mode

    def to_dataframe(self) -> pd.DataFrame:
        """Convert to DataFrame with full trajectory data."""
        data = {
            'most_efficient_project_set': [json.dumps(list(self.most_efficient_project_set))],
            'highest_efficiency_attained': [self.highest_efficiency_attained],
            'final_project_set': [json.dumps(list(self.final_project_set))],
            'final_efficiency': [self.final_efficiency],
            'budget_increase_count': [self.budget_increase_count],
            'budget_increase_list': [json.dumps(self.budget_increase_list)],
            'efficiency_trajectory': [json.dumps(self.efficiency_trajectory)],
            'budget_trajectory': [json.dumps(self.budget_trajectory)],
            'selected_trajectory': [json.dumps(self.selected_trajectory)],
            'monotonic_violation': [self.monotonic_violation],
        }
        return pd.DataFrame(data)


@dataclass
class MESResult:
    """Result container for MES algorithms."""
    selected_projects: List[Any]
    efficiency: float
    budget_increase_count: int

    def to_dataframe(self) -> pd.DataFrame:
        """Convert to DataFrame matching legacy output format."""
        data = {
            'selected_projects': [self.selected_projects],
            'efficiency': [self.efficiency],
            'budget_increase_count': [self.budget_increase_count],
        }
        return pd.DataFrame(data)


# =============================================================================
# EES Completion Implementations
# =============================================================================

def _completion_result_to_ees_result(
    result: CompletionResult,
    actual_budget: Fraction,
    exhaustive: bool = False,
) -> EESResult:
    """Convert a CompletionResult to an EESResult."""
    # Find highest efficiency and corresponding project set
    highest_eff = Fraction(0)
    most_efficient_idx = 0
    exceeded_budget = False
    monotonic_violation = 0

    for i, eff in enumerate(result.efficiency_trajectory):
        # Check if this step is feasible (efficiency <= 1 means cost <= budget)
        if eff <= 1:
            if eff > highest_eff:
                if exceeded_budget and exhaustive:
                    monotonic_violation = 1
                highest_eff = eff
                most_efficient_idx = i
        else:
            exceeded_budget = True

    return EESResult(
        most_efficient_project_set=set(result.outcome.selected),
        highest_efficiency_attained=float(highest_eff),
        final_project_set=set(result.outcome.selected),
        final_efficiency=float(result.outcome.spending_efficiency(actual_budget)),
        budget_increase_count=result.step_count,
        budget_increase_list=[float(d) for d in result.budget_deltas],
        efficiency_trajectory=[float(e) for e in result.efficiency_trajectory],
        budget_trajectory=[float(b) for b in result.budget_trajectory],
        selected_trajectory=result.selected_trajectory,
        monotonic_violation=monotonic_violation,
    )


def run_ees_no_completion(
    election: Election,
    utility,
) -> EESResult:
    """Run EES without any completion - single run."""
    outcome = ees_with_outcome(election, utility)
    efficiency = float(outcome.spending_efficiency(election.budget))

    return EESResult(
        most_efficient_project_set=set(outcome.selected),
        highest_efficiency_attained=efficiency,
        final_project_set=set(outcome.selected),
        final_efficiency=efficiency,
        budget_increase_count=0,
        budget_increase_list=[],
        efficiency_trajectory=[efficiency],
        budget_trajectory=[float(election.budget)],
        selected_trajectory=[len(outcome.selected)],
        monotonic_violation=0,
    )


def run_ees_add_one(
    election: Election,
    utility,
    exhaustive: bool = False,
) -> EESResult:
    """
    Run EES with ADD-ONE completion (increment budget by n each iteration).

    Args:
        election: The election instance
        utility: Utility function (cardinal_utility or cost_utility)
        exhaustive: If True, continue until all projects selected
    """
    if exhaustive:
        result = add_one_complete(election, utility)
    else:
        result = add_one_completion(election, utility)

    return _completion_result_to_ees_result(result, election.budget, exhaustive)


def run_ees_add_opt(
    election: Election,
    utility,
    is_cardinal: bool,
    exhaustive: bool = False,
) -> EESResult:
    """
    Run EES with ADD-OPT completion (optimal budget increment).

    Args:
        election: The election instance
        utility: Utility function (cardinal_utility or cost_utility)
        is_cardinal: True for cardinal utilities, False for cost/uniform
        exhaustive: If True, continue until all projects selected
    """
    if exhaustive:
        result = add_opt_complete(election, utility, is_cardinal)
    else:
        result = add_opt_completion(election, utility, is_cardinal)

    return _completion_result_to_ees_result(result, election.budget, exhaustive)


def run_ees_add_opt_skip(
    election: Election,
    utility,
    is_cardinal: bool,
    exhaustive: bool = False,
) -> EESResult:
    """
    Run EES with ADD-OPT-SKIP completion (heuristic - skip selected projects).

    Args:
        election: The election instance
        utility: Utility function (cardinal_utility or cost_utility)
        is_cardinal: True for cardinal utilities, False for cost/uniform
        exhaustive: If True, continue until all projects selected
    """
    # ADD-OPT-SKIP already explores all projects, so exhaustive is the same
    result = add_opt_skip_completion(election, utility, is_cardinal)

    return _completion_result_to_ees_result(result, election.budget, exhaustive)


# =============================================================================
# MES Implementations
# =============================================================================

def run_mes(
    pabulib_file: str,
    is_cardinal: bool,
    completion: str,
    exhaustive: bool = False,
) -> MESResult:
    """
    Run MES (Method of Equal Shares / Waterflow) algorithm.

    Note: MES uses pabutools directly as there's no equivalent in pb.

    Args:
        pabulib_file: Path to pabulib file
        is_cardinal: True for cardinal/approval, False for cost satisfaction
        completion: 'none' or 'add-one' (MES only supports budget increments of 1)
        exhaustive: If True, continue until all projects selected
    """
    from pabutools.election import parse_pabulib, Cardinality_Sat, Cost_Sat
    from pabutools.rules import method_of_equal_shares

    instance, profile = parse_pabulib(pabulib_file)
    initial_budget = int(instance.budget_limit)
    instance.budget_limit = int(instance.budget_limit)

    sat_class = Cardinality_Sat if is_cardinal else Cost_Sat

    if completion == 'none':
        # Single run without completion
        result = method_of_equal_shares(
            instance=instance,
            profile=profile,
            sat_class=sat_class,
        )
        total_cost = sum(p.cost for p in result)
        efficiency = float(total_cost / initial_budget) if initial_budget > 0 else 0.0

        return MESResult(
            selected_projects=list(result),
            efficiency=efficiency,
            budget_increase_count=0,
        )
    else:
        # Budget exhaustion completion (ADD-ONE style)
        increase_counter = 0
        stop_on_overspend = not exhaustive

        while True:
            result = method_of_equal_shares(
                instance=instance,
                profile=profile,
                sat_class=sat_class,
            )

            total_cost = sum(p.cost for p in result)

            if stop_on_overspend and total_cost > initial_budget:
                break

            if len(result) == len(instance):  # All projects selected
                break

            increase_counter += 1
            instance.budget_limit = instance.budget_limit + 1

        efficiency = float(total_cost / initial_budget) if initial_budget > 0 else 0.0

        return MESResult(
            selected_projects=list(result),
            efficiency=efficiency,
            budget_increase_count=increase_counter,
        )


# =============================================================================
# Main Entry Point
# =============================================================================

def run_pb(
    pabulib_file: str,
    algorithm: str,
    utility: str,
    completion: str,
    exhaustive: bool = False,
) -> pd.DataFrame:
    """
    Run a participatory budgeting algorithm with specified parameters.

    Args:
        pabulib_file: Path to the pabulib (.pb) file
        algorithm: 'ees' or 'mes'
        utility: 'cardinal' (approval) or 'cost' (uniform)
        completion: 'none', 'add-one', 'add-opt', or 'add-opt-skip'
        exhaustive: If True, continue until all projects selected

    Returns:
        DataFrame with results
    """
    is_cardinal = (utility == 'cardinal')

    if algorithm == 'ees':
        # Parse election for EES
        election = parse_pabulib_file(pabulib_file)
        utility_fn = cardinal_utility if is_cardinal else cost_utility

        if completion == 'none':
            result = run_ees_no_completion(election, utility_fn)
        elif completion == 'add-one':
            result = run_ees_add_one(election, utility_fn, exhaustive)
        elif completion == 'add-opt':
            result = run_ees_add_opt(election, utility_fn, is_cardinal, exhaustive)
        elif completion == 'add-opt-skip':
            result = run_ees_add_opt_skip(election, utility_fn, is_cardinal, exhaustive)
        else:
            raise ValueError(f"Unknown completion method: {completion}")

        return result.to_dataframe()

    elif algorithm == 'mes':
        # MES only supports none and add-one completion
        if completion not in ('none', 'add-one'):
            raise ValueError(f"MES only supports 'none' or 'add-one' completion, got: {completion}")

        result = run_mes(pabulib_file, is_cardinal, completion, exhaustive)
        return result.to_dataframe()

    else:
        raise ValueError(f"Unknown algorithm: {algorithm}")


def main():
    """CLI entry point."""
    parser = argparse.ArgumentParser(
        description='Unified Participatory Budgeting CLI',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # EES with cardinal utilities and ADD-OPT completion
  python run_pb.py instance.pb -a ees -u cardinal -c add-opt

  # MES with cost utilities, no completion
  python run_pb.py instance.pb -a mes -u cost -c none

  # EES with ADD-OPT-SKIP heuristic, exhaustive mode
  python run_pb.py instance.pb -a ees -u cost -c add-opt-skip --exhaustive

Completion Methods:
  none         - Single run without budget increases
  add-one      - Increment budget by n (1 per voter) each iteration
  add-opt      - Use optimal budget increment (ADD-OPT algorithm)
  add-opt-skip - Like add-opt but only consider unselected projects (faster)

Note: MES algorithm only supports 'none' and 'add-one' completion methods.
        """
    )

    parser.add_argument('input_file', type=str, help='Path to pabulib (.pb) file')

    parser.add_argument('-a', '--algorithm', type=str, required=True,
                        choices=['ees', 'mes'],
                        help='Algorithm: ees (Exact Equal Shares) or mes (Method of Equal Shares)')

    parser.add_argument('-u', '--utility', type=str, required=True,
                        choices=['cardinal', 'cost'],
                        help='Utility type: cardinal (approval) or cost (uniform)')

    parser.add_argument('-c', '--completion', type=str, required=True,
                        choices=['none', 'add-one', 'add-opt', 'add-opt-skip'],
                        help='Completion method')

    parser.add_argument('--exhaustive', action='store_true',
                        help='Continue until all projects selected (exhaustive mode)')

    parser.add_argument('-o', '--output', type=str, default=None,
                        help='Output file path (default: auto-generated in results/)')

    args = parser.parse_args()

    # Validate input file
    if not os.path.exists(args.input_file):
        print(f"Error: File {args.input_file} not found.")
        sys.exit(1)

    # Validate MES completion methods
    if args.algorithm == 'mes' and args.completion not in ('none', 'add-one'):
        print(f"Error: MES only supports 'none' or 'add-one' completion methods.")
        sys.exit(1)

    # Determine output path
    input_path = Path(args.input_file).resolve()

    if args.output:
        output_path = Path(args.output)
        output_path.parent.mkdir(parents=True, exist_ok=True)
    else:
        # Auto-generate output path
        subdir = f"{args.algorithm}/{args.utility}/{args.completion}"
        if args.exhaustive:
            subdir += "_exhaustive"
        results_dir = setup_results_dir(subdir)
        output_path = results_dir / f"{input_path.stem}.csv"

    print(f"Running PB algorithm:")
    print(f"  Input: {input_path}")
    print(f"  Algorithm: {args.algorithm.upper()}")
    print(f"  Utility: {args.utility}")
    print(f"  Completion: {args.completion}")
    print(f"  Exhaustive: {args.exhaustive}")
    print(f"  Output: {output_path}")

    try:
        df = run_pb(
            pabulib_file=str(input_path),
            algorithm=args.algorithm,
            utility=args.utility,
            completion=args.completion,
            exhaustive=args.exhaustive,
        )

        save_results(df, output_path.parent, output_path.name)
        print(f"\nResults saved to: {output_path}")

        # Print summary
        print("\nSummary:")
        if args.algorithm == 'ees':
            print(f"  Final efficiency: {df['final_efficiency'].iloc[0]:.4f}")
            print(f"  Highest efficiency: {df['highest_efficiency_attained'].iloc[0]:.4f}")
            print(f"  Budget increases (steps): {df['budget_increase_count'].iloc[0]}")
            print(f"  Trajectory length: {len(json.loads(df['efficiency_trajectory'].iloc[0]))}")
        else:
            print(f"  Efficiency: {float(df['efficiency'].iloc[0]):.4f}")
            print(f"  Budget increases: {df['budget_increase_count'].iloc[0]}")
            print(f"  Selected projects: {df['selected_projects'].iloc[0]}")

    except Exception as e:
        print(f"Error during execution: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
