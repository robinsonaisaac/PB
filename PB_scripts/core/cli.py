"""
CLI boilerplate and results handling utilities.

This module provides common infrastructure for running PB experiments
from the command line, including argument parsing, SLURM support,
and results file handling.
"""

import os
import argparse
import traceback
from typing import Callable, Any, Optional
from pathlib import Path


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
    if "SLURM_SUBMIT_DIR" in os.environ:
        base_dir = Path(os.environ["SLURM_SUBMIT_DIR"])
    else:
        # Get the parent of PB_scripts (where results/ should be)
        base_dir = Path(__file__).parent.parent.parent
    
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


def create_argument_parser(description: str = "Run PB experiment") -> argparse.ArgumentParser:
    """
    Create a standard argument parser for PB experiments.
    
    Args:
        description: Description for the argument parser
        
    Returns:
        Configured ArgumentParser
    """
    parser = argparse.ArgumentParser(description=description)
    parser.add_argument("pabulib_file", type=str, help="Path to the pabulib (.pb) file")
    parser.add_argument("--budget", type=int, default=0, 
                       help="Budget override (default: use file budget)")
    return parser


def run_experiment(
    experiment_func: Callable,
    results_subdir: str,
    description: str = "Run PB experiment"
) -> None:
    """
    Run a PB experiment with standard CLI handling.
    
    This is the main entry point for experiment scripts. It handles:
    - Argument parsing
    - Results directory setup
    - Error handling with full tracebacks
    - Results file saving
    
    Args:
        experiment_func: Function that takes (pabulib_file, budget) and returns a DataFrame
        results_subdir: Subdirectory under results/ to save output
        description: Description for help text
    """
    parser = create_argument_parser(description)
    args = parser.parse_args()
    
    results_dir = setup_results_dir(results_subdir)
    
    try:
        df = experiment_func(args.pabulib_file, args.budget)
        
        if df is not None:
            # Generate filename from input file
            input_name = Path(args.pabulib_file).stem
            output_filename = f"{input_name}_results.csv"
            save_results(df, results_dir, output_filename)
            
    except Exception as e:
        print(f"Error running experiment: {e}")
        traceback.print_exc()
        raise


def get_pabulib_files(directory: Path, extension: str = ".pb") -> list:
    """
    Get all pabulib files in a directory.
    
    Args:
        directory: Directory to search
        extension: File extension to match
        
    Returns:
        List of Path objects for matching files
    """
    return sorted(directory.glob(f"*{extension}"))


def calculate_efficiency(total_cost: float, budget: float) -> float:
    """
    Calculate budget efficiency (utilization).
    
    Args:
        total_cost: Total cost of selected projects
        budget: Total available budget
        
    Returns:
        Efficiency as a ratio (0.0 to 1.0)
    """
    if budget == 0:
        return 0.0
    return total_cost / budget

