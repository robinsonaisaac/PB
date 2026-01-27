#!/usr/bin/env python3
"""
Run EES with various configurations.

This is a thin wrapper around the scalable_proportional_pb library,
designed to be compatible with the old experiment scripts.

Usage:
    python scripts/run_ees.py <pabulib_file> [options]

Options:
    --utility {approval,cost}        Utility function (default: approval)
    --completion {none,add-one,add-opt,add-opt-skip}  Completion method (default: none)
    --exhaustive                     Use exhaustive/complete variant
    --output PATH                    Output CSV path (default: results/<input_stem>.csv)
"""

import argparse
import sys
from pathlib import Path

# Add src to path for development
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from scalable_proportional_pb.pabulib_io import parse_pabulib_file, write_results_csv
from scalable_proportional_pb.ees import ees_with_outcome, cardinal_utility, cost_utility
from scalable_proportional_pb.completion import (
    add_one_completion,
    add_opt_completion,
    add_opt_skip_completion,
    add_one_complete,
    add_opt_complete,
    add_opt_skip_complete,
)


def main():
    parser = argparse.ArgumentParser(description="Run EES on a Pabulib file")
    parser.add_argument("input", help="Path to Pabulib .pb file")
    parser.add_argument(
        "--utility",
        choices=["approval", "cost"],
        default="approval",
        help="Utility function (default: approval)"
    )
    parser.add_argument(
        "--completion",
        choices=["none", "add-one", "add-opt", "add-opt-skip"],
        default="none",
        help="Completion heuristic (default: none)"
    )
    parser.add_argument(
        "--exhaustive",
        action="store_true",
        help="Use exhaustive/complete variant"
    )
    parser.add_argument(
        "--output",
        help="Output CSV path (default: results/<input_stem>.csv)"
    )
    
    args = parser.parse_args()
    
    input_path = Path(args.input)
    if not input_path.exists():
        print(f"Error: File not found: {input_path}", file=sys.stderr)
        return 1
    
    # Parse election
    print(f"Parsing: {input_path}")
    election = parse_pabulib_file(str(input_path))
    print(f"  Projects: {election.m}, Voters: {election.n}, Budget: {election.budget}")
    
    # Select utility function
    if args.utility == "cost":
        utility = cost_utility
        is_cardinal = False
    else:
        utility = cardinal_utility
        is_cardinal = True
    
    # Run algorithm
    print(f"Running EES ({args.utility} utility, {args.completion} completion)...")
    
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
    
    # Determine output path
    if args.output:
        output_path = Path(args.output)
    else:
        results_dir = Path(__file__).parent.parent / "results"
        results_dir.mkdir(exist_ok=True)
        output_path = results_dir / f"{input_path.stem}.csv"
    
    # Write results
    write_results_csv(
        str(output_path),
        outcome.selected,
        efficiency,
        budget_increase_count=0,
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

