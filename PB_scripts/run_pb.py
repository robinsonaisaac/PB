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
import pandas as pd
from pathlib import Path
import os
import sys
from dataclasses import dataclass, field
from typing import List, Set, Optional
from fractions import Fraction

# Add src to path for scalable_proportional_pb
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from scalable_proportional_pb import (
    parse_pabulib_file,
    ees_with_outcome,
    add_opt_cardinal,
    add_opt_uniform,
    greedy_project_change_cardinal,
    greedy_project_change_uniform,
)
from scalable_proportional_pb.ees import cardinal_utility, cost_utility
from scalable_proportional_pb.gpc_uniform import compute_L_lists
from scalable_proportional_pb.types import Election, EESOutcome

# =============================================================================
# CLI Helpers
# =============================================================================

def setup_results_dir(subdir: str) -> Path:
    """
    Set up the results directory, with SLURM support.
    
    Uses SLURM_SUBMIT_DIR if running in a SLURM job, otherwise uses
    the script's parent directory.
    
    Args:
        subdir: Subdirectory path under results/
        
    Returns:
        Path to the results directory (created if needed)
    """
    base_dir = Path(__file__).parent.parent
    
    results_dir = base_dir / "results" / subdir
    results_dir.mkdir(parents=True, exist_ok=True)
    
    return results_dir


def save_results(df, filepath: Path, filename: str) -> bool:
    """
    Save DataFrame results to CSV, with fallback to /tmp.
    
    Args:
        df: pandas DataFrame to save
        filepath: Primary save location
        filename: Name of the CSV file
        
    Returns:
        True if saved successfully
    """
    full_path = filepath / filename
    
    try:
        df.to_csv(full_path, index=False)
        return True
    except PermissionError:
        # Fallback to /tmp
        fallback = Path("/tmp") / filename
        df.to_csv(fallback, index=False)
        print(f"Warning: Saved to {fallback} due to permission error")
        return True
    except Exception as e:
        print(f"Error saving results: {e}")
        return False


# =============================================================================
# Result Dataclasses
# =============================================================================

@dataclass
class PBResult:
    """Unified result container for both EES and MES algorithms."""
    most_efficient_project_set: Set[str]
    highest_efficiency_attained: float
    budget_increase_list: List[float] = field(default_factory=list)
    efficiency_list: List[float] = field(default_factory=list)

    def to_dataframe(self) -> pd.DataFrame:
        """Convert to DataFrame with consistent format for all algorithms."""
        data = {
            'most_efficient_project_set': [list(self.most_efficient_project_set)],
            'highest_efficiency_attained': [self.highest_efficiency_attained],
            'budget_increase_list': [self.budget_increase_list],
            'efficiency_list': [self.efficiency_list],
        }
        return pd.DataFrame(data)


# =============================================================================
# EES Completion Implementations
# =============================================================================

def _add_opt_skip_cardinal(election: Election, outcome: EESOutcome) -> Optional[Fraction]:
    """ADD-OPT-SKIP for cardinal utilities: only consider unselected projects."""
    budget_increment: Optional[Fraction] = None
    for p_id in election.projects:
        if p_id not in outcome.selected:
            gpc_increment = greedy_project_change_cardinal(election, outcome, p_id)
            if gpc_increment is not None and gpc_increment > 0:
                if budget_increment is None or gpc_increment < budget_increment:
                    budget_increment = gpc_increment
    return budget_increment


def _add_opt_skip_uniform(election: Election, outcome: EESOutcome, utility) -> Optional[Fraction]:
    """ADD-OPT-SKIP for uniform utilities: only consider unselected projects."""
    L_lists = compute_L_lists(election, outcome, utility)
    budget_increment: Optional[Fraction] = None
    for p_id in election.projects:
        if p_id not in outcome.selected:
            gpc_increment = greedy_project_change_uniform(election, outcome, p_id, utility, L_lists)
            if gpc_increment is not None and gpc_increment > 0:
                if budget_increment is None or gpc_increment < budget_increment:
                    budget_increment = gpc_increment
    return budget_increment


def run_ees_with_completion(
    election: Election,
    utility,
    completion: str,
    is_cardinal: bool = True,
    exhaustive: bool = False,
) -> PBResult:
    """
    Run EES with specified completion method.

    Args:
        election: The election instance
        utility: Utility function (cardinal_utility or cost_utility)
        completion: 'none', 'add-one', 'add-opt', or 'add-opt-skip'
        is_cardinal: True for cardinal utilities, False for cost/uniform
        exhaustive: If True, continue until all projects selected
    """
    actual_budget = election.budget
    n = election.n
    number_total_projects = election.m

    # Initial run
    outcome = ees_with_outcome(election, utility)

    # For completion methods, track efficiency over iterations
    most_efficient_selected = set(outcome.selected)
    efficiency_tracker = float(outcome.spending_efficiency(actual_budget))
    budget_increase_list: List[float] = [0]  # Start with 0 for baseline
    efficiency_list: List[float] = [efficiency_tracker]  # Start with baseline efficiency
    current_budget = election.budget

    # Single run with no completion
    if completion == 'none':
        return PBResult(
            most_efficient_project_set=most_efficient_selected,
            highest_efficiency_attained=efficiency_tracker,
            budget_increase_list=budget_increase_list,
            efficiency_list=efficiency_list,
        )

    # For when using completion methods
    while True:
        if len(outcome.selected) == number_total_projects:
            break

        # Compute budget increment based on completion method
        if completion == 'add-one':
            d = Fraction(actual_budget, 100*n)
        elif completion == 'add-opt':
            if is_cardinal:
                d = add_opt_cardinal(election.with_budget(current_budget), outcome)
            else:
                d = add_opt_uniform(election.with_budget(current_budget), outcome, utility)
        elif completion == 'add-opt-skip':
            if is_cardinal:
                d = _add_opt_skip_cardinal(election.with_budget(current_budget), outcome)
            else:
                d = _add_opt_skip_uniform(election.with_budget(current_budget), outcome, utility)
        else:
            raise ValueError(f"Unknown completion method: {completion}")

        if d is None:  # Infinity - no more changes possible
            break

        current_budget = current_budget + n * d
        budget_increase_list.append(float(d))

        outcome = ees_with_outcome(election.with_budget(current_budget), utility)

        efficiency_candidate = float(outcome.spending_efficiency(actual_budget))
        efficiency_list.append(efficiency_candidate)
        
        if efficiency_candidate > 1:
            if not exhaustive:
                break
        elif efficiency_candidate > efficiency_tracker:
            efficiency_tracker = efficiency_candidate
            most_efficient_selected = set(outcome.selected)

    return PBResult(
        most_efficient_project_set=most_efficient_selected,
        highest_efficiency_attained=efficiency_tracker,
        budget_increase_list=budget_increase_list,
        efficiency_list=efficiency_list,
    )



# =============================================================================
# MES Implementations
# =============================================================================

def run_mes_with_completion(
    pabulib_file: str,
    is_cardinal: bool,
    completion: str,
    exhaustive: bool = False,
) -> PBResult:
    """
    Run MES (Method of Equal Shares / Waterflow) algorithm.

    Note: MES uses pabutools directly as there's no equivalent in scalable_proportional_pb.

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
    number_total_projects = len(instance)
    n = profile.num_ballots()
    # We default to doing what pabutools does, which is increase the budget by 1% per iteration
    add_one_increment = Fraction(1,100)*initial_budget

    sat_class = Cardinality_Sat if is_cardinal else Cost_Sat

    result = method_of_equal_shares(
            instance=instance,
            profile=profile,
            sat_class=sat_class,
        )
    
    # Budget exhaustion completion (ADD-ONE style)
    most_efficient_selected = set(r.name for r in result)
    total_cost = sum(p.cost for p in result)
    efficiency_tracker = float(total_cost / initial_budget) if initial_budget > 0 else 0.0
    increase_counter = 0
    efficiency_list: List[float] = [efficiency_tracker]

    # When no completion
    if completion == "none":
        return PBResult(
        most_efficient_project_set=most_efficient_selected,
        highest_efficiency_attained=efficiency_tracker,
        budget_increase_list=[0],
        efficiency_list=efficiency_list,
    )

    # When using ADD-ONE style completion
    while True:
        if len(result) == number_total_projects:
            break

        instance.budget_limit = instance.budget_limit + add_one_increment
        increase_counter += 1

        result = method_of_equal_shares(
            instance=instance,
            profile=profile,
            sat_class=sat_class,
        )

        total_cost = sum(p.cost for p in result)
        efficiency_candidate = float(total_cost / initial_budget) if initial_budget > 0 else 0.0
        efficiency_list.append(efficiency_candidate)


        if efficiency_candidate > 1:
            if not exhaustive:
                break
        elif efficiency_candidate > efficiency_tracker:
            efficiency_tracker = efficiency_candidate
            most_efficient_selected = set(r.name for r in result)


    return PBResult(
        most_efficient_project_set=most_efficient_selected,
        highest_efficiency_attained=efficiency_tracker,
        budget_increase_list=[0] + [add_one_increment / n] * increase_counter,
        efficiency_list=efficiency_list,
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
        DataFrame with results (consistent format for all algorithms)
    """
    is_cardinal = (utility == 'cardinal')

    if algorithm == 'ees':
        # Parse election for EES
        election = parse_pabulib_file(pabulib_file)
        utility_fn = cardinal_utility if is_cardinal else cost_utility

        result = run_ees_with_completion(
            election, utility_fn, completion, is_cardinal=is_cardinal, exhaustive=exhaustive
        )
        return result.to_dataframe()

    elif algorithm == 'mes':
        # MES only supports none and add-one completion
        if completion not in ('none', 'add-one'):
            raise ValueError(f"MES only supports 'none' or 'add-one' completion, got: {completion}")

        result = run_mes_with_completion(pabulib_file, is_cardinal, completion, exhaustive)
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
        print(f"  Highest efficiency: {df['highest_efficiency_attained'].iloc[0]:.4f}")
        print(f"  Projects selected: {len(df['most_efficient_project_set'].iloc[0])}")
        print(f"  Budget increases: {len(df['budget_increase_list'].iloc[0]) - 1}")
    except Exception as e:
        print(f"Error during execution: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
