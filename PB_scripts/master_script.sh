#!/bin/bash
#SBATCH --account=p33118  ## Required: your Slurm account name, i.e. eXXXX, pXXXX or bXXXX
#SBATCH --partition=normal ## Required: buyin, short, normal, long, gengpu, genhimem, etc.
#SBATCH --time=48:00:00       ## Required: How long will the job need to run?  Limits vary by partition
#SBATCH --nodes=1             ## How many computers/nodes do you need? Usually 1
#SBATCH --array=0-775     ## Parallelizing by creating a slurm job for each file. Use command (ls ../Data/*.pb | wc -l) to count how many files
#SBATCH --cpus-per-task=1    # Do not have to use --ntasks since we are parallelizing with array (embarassingly parallel)
#SBATCH --mem-per-cpu=2G              ## How much RAM do you need per computer/node? G = gigabytes
#SBATCH --mail-type=ALL ## BEGIN, END, FAIL, or ALL
#SBATCH --mail-user=mattcasey@u.northwestern.edu
#SBATCH --output=../slurm_outputs/%x/%A/%a.out  ## This gives job_name/master_job_id/array_task_index

# Unified SLURM submission script for Participatory Budgeting experiments
#
# Usage:
#   ./master_script.sh -a <algorithm> -u <utility> -c <completion> [-e]
#
# Arguments:
#   -a, --algorithm     Algorithm: ees or mes
#   -u, --utility       Utility type: cardinal or cost
#   -c, --completion    Completion method: none, add-one, add-opt, add-opt-skip
#   -e, --exhaustive    Enable exhaustive mode (continue until all projects selected)
#   -s, --script-dir    Directory containing run_pb.py (auto-detected)
#   -h, --help          Show this help message
#
# Examples:
#   # EES with cardinal utilities and ADD-OPT completion
#   ./master_script.sh -a ees -u cardinal -c add-opt
#
#   # MES with cost utilities, exhaustive mode
#   ./master_script.sh -a mes -u cost -c add-one -e
#
#   # EES with ADD-OPT-SKIP heuristic
#   ./master_script.sh -a ees -u cardinal -c add-opt-skip
#

set -e

# Default values
ALGORITHM=""
UTILITY=""
COMPLETION=""
EXHAUSTIVE=""
SCRIPT_DIR=""

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        -a|--algorithm)
            ALGORITHM="$2"
            shift 2
            ;;
        -u|--utility)
            UTILITY="$2"
            shift 2
            ;;
        -c|--completion)
            COMPLETION="$2"
            shift 2
            ;;
        -e|--exhaustive)
            EXHAUSTIVE="--exhaustive"
            shift
            ;;
        -s|--script-dir)
            SCRIPT_DIR="$2"
            shift 2
            ;;
        -h|--help)
            sed -n '12,37p' "$0"
            exit 0
            ;;
        *)
            echo "Unknown option: $1"
            exit 1
            ;;
    esac
done

# Validate required arguments
if [[ -z "$ALGORITHM" ]] || [[ -z "$UTILITY" ]] || [[ -z "$COMPLETION" ]] ; then
    echo "Error: Missing required arguments"
    echo "Usage: $0 -a <algorithm> -u <utility> -c <completion> -d <data_dir>"
    echo "Run '$0 --help' for more information"
    exit 1
fi

# Validate algorithm
if [[ "$ALGORITHM" != "ees" ]] && [[ "$ALGORITHM" != "mes" ]]; then
    echo "Error: Algorithm must be 'ees' or 'mes', got: $ALGORITHM"
    exit 1
fi

# Validate utility
if [[ "$UTILITY" != "cardinal" ]] && [[ "$UTILITY" != "cost" ]]; then
    echo "Error: Utility must be 'cardinal' or 'cost', got: $UTILITY"
    exit 1
fi

# Validate completion
if [[ "$COMPLETION" != "none" ]] && [[ "$COMPLETION" != "add-one" ]] && [[ "$COMPLETION" != "add-opt" ]] && [[ "$COMPLETION" != "add-opt-skip" ]]; then
    echo "Error: Completion must be 'none', 'add-one', 'add-opt', or 'add-opt-skip', got: $COMPLETION"
    exit 1
fi

# MES only supports none and add-one
if [[ "$ALGORITHM" == "mes" ]] && [[ "$COMPLETION" != "none" ]] && [[ "$COMPLETION" != "add-one" ]]; then
    echo "Error: MES only supports 'none' or 'add-one' completion methods"
    exit 1
fi

# Auto-detect script directory if not specified
if [[ -z "$SCRIPT_DIR" ]]; then
    # Try to find run_pb.py relative to this script
    SCRIPT_DIR="$(dirname "$(realpath "$0")")"
    if [[ ! -f "$SCRIPT_DIR/run_pb.py" ]]; then
          echo "Error: Cannot find run_pb.py. Use -s to specify script directory."
          exit 1
    fi
fi

RUN_PB_PATH="$SCRIPT_DIR/run_pb.py"

echo "=============================================="
echo "Submitting PB jobs with configuration:"
echo "  Algorithm:   $ALGORITHM"
echo "  Utility:     $UTILITY"
echo "  Completion:  $COMPLETION"
echo "  Exhaustive:  ${EXHAUSTIVE:-no}"
echo "  Script:      $RUN_PB_PATH"
echo "=============================================="

# Working under the assumption that a virtualenvironment exists with
# the proper python version and pabutools and pandas installed
#module load python/3.12.10
#source ../.venv/bin/activate

# Folder containing files
FILES_DIR="../Data"

# Build a bash array of files
FILES=("$FILES_DIR"/*.pb)

# Pick the file corresponding to this array task
FILE="${FILES[110]}"

echo "Running on file: $FILE"
#echo "Array task ID: $SLURM_ARRAY_TASK_ID"

python3 $RUN_PB_PATH $FILE -a $ALGORITHM -u $UTILITY -c $COMPLETION $EXHAUSTIVE