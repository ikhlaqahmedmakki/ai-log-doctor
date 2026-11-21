#!/usr/bin/env bash
# Copy the last 100 ERROR lines from a log file into reports/latest_snapshot.txt.
set -euo pipefail

root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
snapshot="${root}/reports/latest_snapshot.txt"

if [[ $# -ne 1 ]]; then
  echo "Usage: $(basename "$0") <log-file>" >&2
  exit 1
fi

log_file="$1"

if [[ ! -f "$log_file" ]]; then
  echo "Log file not found: ${log_file}" >&2
  exit 1
fi

if [[ ! -r "$log_file" ]]; then
  echo "Log file is not readable: ${log_file}" >&2
  exit 1
fi

mkdir -p "${root}/reports"

# grep exits 1 when nothing matches. That is an empty snapshot, not a failure.
# Exit 2 means grep could not read the file.
set +e
grep -w -F -- 'ERROR' "$log_file" | tail -n 100 > "$snapshot"
grep_status=${PIPESTATUS[0]}
set -e

if [[ "$grep_status" -eq 2 ]]; then
  echo "Failed to read log file: ${log_file}" >&2
  exit 1
fi

if [[ "$grep_status" -ne 0 && "$grep_status" -ne 1 ]]; then
  echo "Failed while filtering ERROR lines from: ${log_file}" >&2
  exit 1
fi
