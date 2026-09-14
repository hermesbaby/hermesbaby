#!/usr/bin/env bash
# Source this file from Bash: source ./run_parallel.sh
# Each argument is a command string interpreted by a separate `bash -c`.
# Runs all commands concurrently and waits for all direct children.
# Returns the first nonzero status in argument order, or 0 on full success.
# Nested calls work through Bash's exported-function mechanism.
# See run_parallel.md for examples, quoting, and limitations.

run_parallel() {
    export -f run_parallel

    local command pid code
    local exit_code=0
    local -a pids=()

    # Launch every command before waiting for any command.
    for command in "$@"; do
        printf 'Starting: %s\n' "$command"
        bash -c "$command" &
        pids+=("$!")
    done

    # Collect statuses in launch order without stopping on failure.
    for pid in "${pids[@]}"; do
        if wait "$pid"; then
            :
        else
            code=$?
            if (( exit_code == 0 )); then
                exit_code=$code
            fi
        fi
    done

    if (( exit_code != 0 )); then
        return "$exit_code"
    fi

    printf '\nAll have run successfully\n'
    return 0
}
