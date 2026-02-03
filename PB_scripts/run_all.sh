#!/bin/bash
# EES Cardinal (3 completion options, exhaustive/not-exhaustive)
# sbatch --job-name=ees_approval_none --partition=normal --time=24:00:00 master_script.sh -a ees -u cardinal -c none
sbatch --job-name=ees_cardinal_add_one --partition=long --time=168:00:00 master_script.sh -a ees -u cardinal -c add-one
sbatch --job-name=ees_cardinal_add_one_exhaustive --partition=long --time=168:00:00 master_script.sh -a ees -u cardinal -c add-one -e
sbatch --job-name=ees_cardinal_add_opt --partition=long --time=168:00:00 master_script.sh -a ees -u cardinal -c add-opt
sbatch --job-name=ees_cardinal_add_opt_exhaustive --partition=long --time=168:00:00 master_script.sh -a ees -u cardinal -c add-opt -e
sbatch --job-name=ees_cardinal_add_opt_skip --partition=long --time=168:00:00 master_script.sh -a ees -u cardinal -c add-opt-skip
sbatch --job-name=ees_cardinal_add_opt_skip_exhaustive --partition=long --time=168:00:00 master_script.sh -a ees -u cardinal -c add-opt-skip -e

# EES cost (3 completion options, exhaustive/not-exhaustive)
sbatch --job-name=ees_cost_none --partition=short --time=1:00:00 master_script.sh -a ees -u cost -c none
sbatch --job-name=ees_cost_add_one --partition=long --time=168:00:00 master_script.sh -a ees -u cost -c add-one
sbatch --job-name=ees_cost_add_one_exhaustive --partition=long --time=168:00:00 master_script.sh -a ees -u cost -c add-one -e
sbatch --job-name=ees_cost_add_opt --partition=long --time=168:00:00 master_script.sh -a ees -u cost -c add-opt
sbatch --job-name=ees_cost_add_opt_exhaustive --partition=long --time=168:00:00 master_script.sh -a ees -u cost -c add-opt -e
sbatch --job-name=ees_cost_add_opt_skip --partition=long --time=168:00:00 master_script.sh -a ees -u cost -c add-opt-skip
sbatch --job-name=ees_cost_add_opt_skip_exhaustive --partition=long --time=168:00:00 master_script.sh -a ees -u cost -c add-opt-skip -e

# MES Cardinal (1 completion option, exhaustive/not-exhaustive)
sbatch --job-name=mes_cardinal_none --partition=short --time=1:00:00 master_script.sh -a mes -u cardinal -c none
sbatch --job-name=mes_cardinal_add_one --partition=long --time=168:00:00 master_script.sh -a mes -u cardinal -c add-one
sbatch --job-name=mes_cardinal_add_one_exhaustive --partition=long --time=168:00:00 master_script.sh -a mes -u cardinal -c add-one -e

# MES cost (1 completion option, exhaustive/not-exhaustive)
sbatch --job-name=mes_cost_none --partition=short --time=1:00:00 master_script.sh -a mes -u cost -c none
sbatch --job-name=mes_cost_add_one --partition=long --time=168:00:00 master_script.sh -a mes -u cost -c add-one
sbatch --job-name=mes_cost_add_one_exhaustive --partition=long --time=168:00:00 master_script.sh -a mes -u cost -c add-one -e
