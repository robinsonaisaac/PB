#!/bin/bash
ARRAY_JOBID="$1"

# Get job name for directory
JOBNAME=$(sacct -j "$ARRAY_JOBID" --format=JobName%60 --noheader | head -n 1 | xargs)
OUTDIR=$(echo "$JOBNAME" | tr ' /' '__')
mkdir -p "$OUTDIR"

HEADER="JobID,State,Elapsed,TotalCPU,AllocCPUS,MaxRSS,ReqMem"

# Get only "clean" array task IDs: 123456_0, 123456_1, ...
TASK_IDS=$(sacct -j "$ARRAY_JOBID" --format=JobID --noheader \
           | awk '{$1=$1; print $1}' \
           | grep -E "^${ARRAY_JOBID}_[0-9]+$")


for JOB in $TASK_IDS; do
    ARRAY_IDX="${JOB##*_}"   # 7606229_42 → 42
    echo "  → Saving sacct for task $ARRAY_IDX"
    {
        echo "$HEADER"
        sacct -j "$JOB" \
            --format=JobID,State,Elapsed,TotalCPU,AllocCPUS,MaxRSS,ReqMem \
            --parsable2 --noheader \
	   | grep -vE '\.(batch|extern)$'
    } > "$OUTDIR/${ARRAY_IDX}.csv"
done

echo "Done. Reports saved in: $OUTDIR"
