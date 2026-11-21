#!/usr/bin/env bash
# scripts/run_doctor.sh
# Usage: ./scripts/run_doctor.sh <path-to-log-file>
#
# Collects logs using collect_logs.sh and runs the AI doctor diagnosis if collection succeeds.

set -euo pipefail

if [ $# -eq 0 ]; then
    echo "Error: No log file path provided."
    echo "Usage: $0 <path-to-log-file>"
    exit 1
fi

LOG_FILE="$1"

# Step 1: Collect logs
echo "Collecting logs from: $LOG_FILE"
bash scripts/collect_logs.sh "$LOG_FILE"

# Step 2: Run doctor diagnosis
echo "Running AI doctor diagnosis..."
python src/doctor.py

echo "Doctor run completed successfully."
