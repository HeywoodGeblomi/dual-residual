#!/usr/bin/env bash
# Reproduce the Job 2 Monte Carlo null sweep from the repo root.
# Modest by design: coverage probe, tie-rate pilot, 4000-trial official grid.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
cd "$ROOT"
mkdir -p validation/job2_null_sweep/data validation/job2_null_sweep/plots
g++ -std=c++17 -O2 -Wall -Wextra -I. \
  validation/job2_null_sweep/sweep_null.cpp -o /tmp/job2_sweep_null
g++ -std=c++17 -O2 -Wall -Wextra -I. \
  validation/job2_null_sweep/classical_t1_probe.cpp -o /tmp/job2_classical_t1
/tmp/job2_classical_t1 | tee validation/job2_null_sweep/data/classical_t1_probe.txt
/tmp/job2_sweep_null coverage validation/job2_null_sweep/data/coverage.csv
/tmp/job2_sweep_null pilot validation/job2_null_sweep/data/pilot_tie_rates.csv
python3 validation/job2_null_sweep/select_rw_step.py --check
/tmp/job2_sweep_null run /tmp/job2_det_a.csv 10
/tmp/job2_sweep_null run /tmp/job2_det_b.csv 10
cmp /tmp/job2_det_a.csv /tmp/job2_det_b.csv
rm -f /tmp/job2_det_a.csv /tmp/job2_det_b.csv
/tmp/job2_sweep_null run validation/job2_null_sweep/data/null_trials.csv
python3 validation/job2_null_sweep/analyze_null.py
(
  cd validation/job2_null_sweep
  sha256sum data/coverage.csv data/pilot_tie_rates.csv data/null_trials.csv \
    data/summary_by_cell.csv data/fpr_by_event_count.csv data/fit.json \
    data/classical_vs_tie.csv data/classical_identity.json \
    data/classical_t1_probe.txt \
    > data/SHA256SUMS
)
echo "dual_residual.hpp blob $(git rev-parse HEAD:dual_residual.hpp)"
echo "HEAD $(git rev-parse HEAD)"
