"""
CLI entry point for scalable-proportional-pb.

Usage:
    python -m pb run --input <file.pb> [options]
"""

import argparse
import sys
from fractions import Fraction
from pathlib import Path

from .pabulib_io import parse_pabulib_file, write_results_csv
from .ees import ees_with_outcome, cardinal_utility, cost_utility
from .completion import (
    add_one_completion,
    add_opt_completion,
    add_opt_skip_completion,
    add_one_complete,
    add_opt_complete,
    add_opt_skip_complete,
)


def main():
    parser = argparse.ArgumentParser(
        description="Exact Equal Shares (EES) for participatory budgeting"
    )
    subparsers = parser.add_subparsers(dest="command", help="Command to run")
    
    # Run command
    run_parser = subparsers.add_parser("run", help="Run EES on a Pabulib file")
    run_parser.add_argument(
        "--input", "-i",
        required=True,
        help="Path to Pabulib .pb file"
    )
    run_parser.add_argument(
        "--output", "-o",
        help="Output CSV path (default: <input_stem>.csv)"
    )
    run_parser.add_argument(
        "--utility",
        choices=["approval", "cost"],
        default="approval",
        help="Utility function: approval (cardinal) or cost"
    )
    run_parser.add_argument(
        "--completion",
        choices=["none", "add-one", "add-opt", "add-opt-skip"],
        default="none",
        help="Completion heuristic"
    )
    run_parser.add_argument(
        "--exhaustive",
        action="store_true",
        help="Use exhaustive/complete variant (continue until all projects selected)"
    )
    
    args = parser.parse_args()
    
    if args.command is None:
        parser.print_help()
        return 1
    
    if args.command == "run":
        return run_command(args)
    
    return 0


def run_command(args):
    """Execute the run command."""
    input_path = Path(args.input)
    if not input_path.exists():
        print(f"Error: File not found: {input_path}", file=sys.stderr)
        return 1
    
    # Parse election
    print(f"Parsing: {input_path}")
    election = parse_pabulib_file(str(input_path))
    print(f"  Projects: {election.m}")
    print(f"  Voters: {election.n}")
    print(f"  Budget: {election.budget}")
    
    # Select utility function
    if args.utility == "cost":
        utility = cost_utility
        is_cardinal = False
    else:
        utility = cardinal_utility
        is_cardinal = True
    
    # Run algorithm
    print(f"Running EES with {args.utility} utility...")
    
    if args.completion == "none":
        outcome = ees_with_outcome(election, utility)
    elif args.completion == "add-one":
        if args.exhaustive:
            outcome = add_one_complete(election, utility)
        else:
            outcome = add_one_completion(election, utility)
    elif args.completion == "add-opt":
        if args.exhaustive:
            outcome = add_opt_complete(election, utility, is_cardinal)
        else:
            outcome = add_opt_completion(election, utility, is_cardinal)
    elif args.completion == "add-opt-skip":
        if args.exhaustive:
            outcome = add_opt_skip_complete(election, utility, is_cardinal)
        else:
            outcome = add_opt_skip_completion(election, utility, is_cardinal)
    
    # Report results
    efficiency = outcome.spending_efficiency(election.budget)
    print(f"\nResults:")
    print(f"  Selected: {len(outcome.selected)} projects")
    print(f"  Total cost: {float(outcome.total_cost):.2f}")
    print(f"  Efficiency: {float(efficiency):.4f}")
    print(f"  Projects: {sorted(outcome.selected)}")
    
    # Write output
    if args.output:
        output_path = Path(args.output)
    else:
        output_path = input_path.with_suffix(".csv")
    
    write_results_csv(
        str(output_path),
        outcome.selected,
        efficiency,
        budget_increase_count=0,  # TODO: track this
        additional_data={
            "total_cost": float(outcome.total_cost),
            "utility": args.utility,
            "completion": args.completion,
            "exhaustive": args.exhaustive,
        }
    )
    print(f"\nResults written to: {output_path}")
    
    return 0


if __name__ == "__main__":
    sys.exit(main())

