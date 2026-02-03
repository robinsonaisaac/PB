#!/bin/bash
sbatch --job-name=ees_approval_none --partition=short --time=24:00:00 master_script.sh -a ees -u cost -c none