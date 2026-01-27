---
name: Refactor PB_scripts Deduplication
overview: Extract duplicated code from 17 PB_scripts files into shared modules while preserving the existing script structure. This will reduce code duplication from ~8000 lines to ~2000 lines and make maintenance easier.
todos:
  - id: create-core-package
    content: Create PB_scripts/core/ package with __init__.py
    status: completed
  - id: extract-utils
    content: Create core/utils.py with profile_preprocessing, utility functions
    status: completed
    dependencies:
      - create-core-package
  - id: extract-ees
    content: Create core/ees.py with EES implementations (approval + uniform)
    status: completed
    dependencies:
      - extract-utils
  - id: extract-add-opt
    content: Create core/add_opt.py with GPC and ADD-OPT implementations
    status: completed
    dependencies:
      - extract-ees
  - id: extract-cli
    content: Create core/cli.py with CLI boilerplate and results handling
    status: completed
    dependencies:
      - create-core-package
  - id: update-approval-scripts
    content: Update run_approval_equal_shares_*.py files to use core modules
    status: completed
    dependencies:
      - extract-ees
      - extract-add-opt
      - extract-cli
  - id: update-cost-scripts
    content: Update run_cost_equal_shares_*.py files to use core modules
    status: completed
    dependencies:
      - extract-ees
      - extract-add-opt
      - extract-cli
  - id: update-waterflow-scripts
    content: Update run_*_waterflow_*.py files to use core modules
    status: completed
    dependencies:
      - extract-cli
  - id: cleanup
    content: Remove dead code, debug prints, and exact_equal_shares_cost_module.py
    status: completed
    dependencies:
      - update-approval-scripts
      - update-cost-scripts
      - update-waterflow-scripts
---

# Refactor PB_scripts: Extract Shared Modules

## Problem Analysis

The `PB_scripts/` folder contains 17 Python files with massive code duplication:

- `profile_preprocessing()` - duplicated 10+ times
- `exact_method_of_equal_shares_*()` - duplicated 8+ times  
- `greedy_project_change_*()` - duplicated 6+ times
- `add_opt_*()` - duplicated 6+ times
- CLI boilerplate (argparse, results dir, error handling) - duplicated in every file

## Refactoring Strategy

Create 4 shared modules in `PB_scripts/` and update all runner scripts to import from them.

---

## New Shared Modules

### 1. `PB_scripts/core/utils.py` - Common Utilities

```python
# Extract:
- profile_preprocessing()
- cost_utility() / cardinal_utility()
- filter_sd()
- calculate_bang_per_buck()
```

### 2. `PB_scripts/core/ees.py` - EES Implementations

```python
# Extract from run_approval_equal_shares*.py and run_cost_equal_shares*.py:
- exact_method_of_equal_shares_approval()
- exact_method_of_equal_shares_uniform()
# Parameterize by utility function to avoid duplication
```

### 3. `PB_scripts/core/add_opt.py` - ADD-OPT Implementations

```python
# Extract:
- greedy_project_change_approvals()
- greedy_project_change_uniform()
- add_opt_approval() / add_opt_approval_heuristic()
- add_opt_cost() / add_opt_cost_heuristic()
```

### 4. `PB_scripts/core/cli.py` - CLI Boilerplate

```python
# Extract:
- Argument parsing setup
- Results directory creation (with SLURM support)
- Error handling wrapper
- Output saving with fallback
```

---

## Updated Runner Scripts

Each runner script (e.g., `run_approval_equal_shares_exhaustive_heuristic.py`) becomes ~50 lines:

```python
from core.utils import profile_preprocessing
from core.ees import exact_method_of_equal_shares
from core.add_opt import add_opt_approval_heuristic
from core.cli import run_experiment, save_results

def main(pabulib_file, budget=0):
    # ~20 lines of experiment-specific logic
    ...

if __name__ == "__main__":
    run_experiment(main, results_subdir="exact_equal_shares/approval/...")
```

---

## Files to Modify

| File | Change |

|------|--------|

| `PB_scripts/core/__init__.py` | NEW - Package init |

| `PB_scripts/core/utils.py` | NEW - Common utilities |

| `PB_scripts/core/ees.py` | NEW - EES algorithms |

| `PB_scripts/core/add_opt.py` | NEW - ADD-OPT algorithms |

| `PB_scripts/core/cli.py` | NEW - CLI helpers |

| `run_approval_equal_shares*.py` (4 files) | UPDATE - Import from core |

| `run_cost_equal_shares*.py` (4 files) | UPDATE - Import from core |

| `run_*_waterflow*.py` (6 files) | UPDATE - Import from core |

| `exact_equal_shares_cost_module.py` | REMOVE - Merge into core/ees.py |

---

## Cleanup Tasks

1. Remove all commented-out code blocks
2. Remove debug `print()` statements (or convert to proper logging)
3. Standardize docstrings
4. Add type hints to shared modules