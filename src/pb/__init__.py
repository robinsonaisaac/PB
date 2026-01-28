"""
Scalable Proportional Participatory Budgeting

Implements the Exact Equal Shares (EES) method and completion heuristics
(ADD-OPT, ADD-OPT-SKIP, ADD-ONE) from the paper:
"Streamlining Equal Shares" (arXiv:2502.11797)

Tie-breaking: lexicographic by project id/name.
"""

from .types import Project, Election, EESOutcome, CompletionResult
from .ees import ees, ees_with_outcome
from .gpc_cardinal import greedy_project_change_cardinal
from .add_opt_cardinal import add_opt_cardinal
from .gpc_uniform import greedy_project_change_uniform
from .add_opt_uniform import add_opt_uniform
from .completion import (
    add_one_completion,
    add_opt_completion,
    add_opt_skip_completion,
    add_one_complete,
    add_opt_complete,
    add_opt_skip_complete,
)
from .pabulib_io import parse_pabulib_file

__all__ = [
    "Project",
    "Election",
    "EESOutcome",
    "CompletionResult",
    "ees",
    "ees_with_outcome",
    "greedy_project_change_cardinal",
    "add_opt_cardinal",
    "greedy_project_change_uniform",
    "add_opt_uniform",
    "add_one_completion",
    "add_opt_completion",
    "add_opt_skip_completion",
    "add_one_complete",
    "add_opt_complete",
    "add_opt_skip_complete",
    "parse_pabulib_file",
]

