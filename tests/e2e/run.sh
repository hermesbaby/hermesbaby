#!/usr/bin/env bash

# Get all test*.sh files in the directory where this script is located and execute them in the alphabetical order of their names
# Per default it finishes on the first script exiting with a non-zero exit code
# In case of argument "--continue" all scripts are executed even if some fail

set -euo pipefail

# In case CTLR-C the entire script is aborted
trap "exit" INT

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
SCRIPT_NAME="$(basename "$0")"

# Log all output to a temporary log file
log_file=$(mktemp /tmp/$SCRIPT_NAME-XXXXXX.log)
exec > >(tee -a "$log_file") 2>&1
echo "Logging to file: $log_file"

CONTINUE=false
for arg in "$@"; do
    if [ "$arg" == "--continue" ]; then
        CONTINUE=true
    fi
done



RET_CODE=0

# The glob test*.sh is sorted alphabetically by bash
for test_script in "$SCRIPT_DIR"/test*.sh; do
    # Skip if no files match the glob
    [ -e "$test_script" ] || continue

    # Skip the script itself
    if [ "$(basename "$test_script")" == "$SCRIPT_NAME" ]; then
        continue
    fi

    echo "Running $test_script..."
    if ! bash "$test_script"; then
        echo "Test $test_script failed"
        RET_CODE=1
        if [ "$CONTINUE" = false ]; then
            exit 1
        fi
    fi
done

exit $RET_CODE
