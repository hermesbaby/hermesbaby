# Running command groups in parallel with Bash

`run_parallel.sh` provides a reusable `run_parallel` function. Pass one shell command string per argument: it starts them concurrently, waits for all of them, and reports success only if all return zero. Nested groups allow independent sequences of dependent work.

## 1. Load the function

Use Bash, not POSIX `sh`. The implementation uses Bash arrays, `local`, and exported functions. It does not require GNU Parallel or newer `wait -n` options.

Place both files in your working directory, then load the function:

```bash
source ./run_parallel.sh
```

Sourcing defines the function in the current shell. Running `bash run_parallel.sh` only defines it in a temporary shell and performs no jobs. No executable permission is required when sourcing.

For a standalone driver, create a Bash script:

```bash
#!/usr/bin/env bash
source ./run_parallel.sh

run_parallel \
    'sleep 2 && echo "First finished"' \
    'sleep 1 && echo "Second finished"' \
    || exit "$?"
```

Run the driver with `bash driver.sh`. This example assumes the current directory contains `run_parallel.sh`. To source relative to the driver instead, use:

```bash
source "$(dirname -- "${BASH_SOURCE[0]}")/run_parallel.sh"
```

## 2. Contract

```bash
run_parallel 'command line 1' 'command line 2' ...
```

| Behavior | Meaning |
| --- | --- |
| Input | Each argument is a complete Bash command string, not one word of a single command. |
| Launch | Every argument starts in a separate `bash -c` process before waiting begins. |
| Waiting | The function waits for every launched direct child, even after a failure. |
| Success | Prints `All have run successfully` and returns `0`. |
| Failure | Suppresses that group's success message and returns the first nonzero status in argument order. |
| Empty list | Prints the success message and returns `0`; there are no failed jobs. |
| Output | Starting messages and child output use the caller's streams and may interleave. |
| Nesting | The function exports itself, so child Bash processes can call it. |

This is **wait-for-all**, not immediate failure termination. It neither stops sibling jobs nor returns immediately when a command fails. The function uses `return`; the caller decides whether to exit its own script.

## 3. A list of commands

```bash
commands=(
    'sleep 2 && echo "Job A finished"'
    'sleep 1 && echo "Job B finished"'
    'sleep 3 && echo "Job C finished"'
)

run_parallel "${commands[@]}" || exit "$?"
```

These jobs take approximately three seconds in total, plus process and output overhead. The quoted array expansion preserves every element as one argument.

The same tool can use different arguments:

```bash
commands=(
    'ping -c 1 example.com'
    'ping -c 2 github.com'
    'ping -c 3 localhost'
)

run_parallel "${commands[@]}" || exit "$?"
```

The ping example assumes a Unix-style `ping` supporting `-c` and working network access. The sleep examples need no network.

## 4. How the implementation works

The launch loop uses these two lines:

```bash
bash -c "$command" &
pids+=("$!")
```

`&` starts the child asynchronously. `$!` is its process ID, which is added to the local array. Bash can immediately start the next child.

The second loop calls `wait "$pid"` for each saved PID. Waiting suspends the parent, not the other jobs. If a child has already finished, Bash can return its saved status immediately.

| Job | Completion time from launch | Status |
| --- | ---: | ---: |
| A | 5 seconds | 0 |
| B | 2 seconds | 7 |
| C | 8 seconds | 0 |

Waiting for A lasts until second five. Waiting for B then returns `7` immediately. Waiting for C lasts until second eight. All results have now been collected, and the group returns `7`.

`if wait "$pid"` selects the success or failure branch. In the failure branch, `code=$?` immediately saves the status. The function only updates `exit_code` while it is zero, preserving the first failure in list order. It keeps waiting after that failure.

Do not replace this with an unqualified `wait`: that waits for all background jobs but does not provide the individual failure statuses needed here. Also avoid `if ! wait ...; then code=$?`: `!` inverts the status, so `$?` would no longer be the child's original failure code.

## 5. Handle failure explicitly

Exit the driver with the group's result:

```bash
run_parallel 'sleep 1; exit 7' 'sleep 2; echo "Still completed"' || exit "$?"
```

The second command finishes before the function returns `7`. There is no success message from this group.

Or handle the result without exiting:

```bash
if run_parallel 'exit 7' 'true'; then
    echo "Continue with dependent work"
else
    status=$?
    printf 'Group failed with status %s\n' "$status" >&2
fi
```

Capture `$?` before another command changes it. Do not rely on a caller's `set -e` to determine how command strings run in new Bash processes; express dependencies explicitly with `&&` or `|| exit "$?"`.

When several jobs fail, **list order decides**, not the order in which they finish:

```bash
run_parallel 'sleep 2; exit 7' 'exit 9' || exit "$?"
```

This returns `7` after the first job finishes, although the second job failed earlier. Normal shell status conventions apply: command-not-found generally produces `127`, and signal termination is represented by Bash using a status greater than `128`.

## 6. Two nested groups: two jobs and three jobs

```bash
run_parallel \
    'run_parallel "sleep 2 && echo A1" "sleep 1 && echo A2"' \
    'run_parallel "sleep 1 && echo B1" "sleep 2 && echo B2" "sleep 3 && echo B3"' \
    || exit "$?"
```

All five leaf jobs can run concurrently. Each inner group waits for its own jobs. The outer group waits for both inner groups. All function variables are local to each invocation, so their PID arrays and recorded statuses do not interfere.

`export -f run_parallel` is inside the function. Bash passes the function definition to child Bash processes through the environment, enabling deeper nesting without a separate export step. This depends on child Bash allowing imported functions; privilege-changing or environment-sanitizing wrappers can prevent it.

Compared with a flat group of five independent jobs, nesting adds two group shell processes and group completion boundaries. With this order and no extra steps, it selects the same failure status as a flat list. If everything succeeds, the two inner groups and the outer group each print a success message: three messages in total.

## 7. Use `&&` for dependent work

Grouping is useful when each branch has a follow-up that must wait for its own prerequisites:

```bash
run_parallel \
    'run_parallel "sleep 2 && echo A1" "sleep 1 && echo A2" && echo "Group A follow-up"' \
    'run_parallel "sleep 1 && echo B1" "sleep 2 && echo B2" "sleep 3 && echo B3" && echo "Group B follow-up"' \
    || exit "$?"
```

Group A's follow-up starts only after A1 and A2 succeed. Group B proceeds independently. The outer call waits for both complete branches, including their follow-ups.

If an inner group fails, `&&` skips its follow-up and the branch retains the group's failure status. If the follow-up runs, its status becomes the branch's status.

A build workflow could look like this, assuming these scripts exist:

```bash
run_parallel \
    'run_parallel "./build_api.sh" "./build_worker.sh" && ./test_backend.sh' \
    'run_parallel "./build_web.sh" "./check_styles.sh" "./check_types.sh" && ./test_frontend.sh' \
    && ./package_release.sh
```

Backend tests wait for both backend builds. Frontend tests wait for all three frontend jobs. Packaging runs only when both complete branches succeed.

### A semicolon can hide a failure

```bash
# The final echo succeeds, so this entire command string returns 0:
run_parallel 'false; echo "Done"'

# The echo is skipped, preserving the failure:
run_parallel 'false && echo "Done"'
```

The function observes each child shell's final status, not every command executed inside it. The same rule applies to nested groups. For more steps, propagate failure explicitly:

```bash
run_parallel \
    'run_parallel "true" "false" || exit "$?"; echo "Only after success"' \
    'sleep 1 && echo "Independent branch"'
```

## 8. Quoting, variables, and arguments

### Filenames containing spaces

Use outer single quotes for the command string and inner double quotes for a filename:

```bash
run_parallel \
    'wc -c "first input.txt"' \
    'wc -c "second input.txt"'
```

Each string is parsed by the child Bash. Outer single quotes defer `$variable` expansion and command substitutions to that child.

### Export variables needed by children

```bash
export INPUT_FILE='file with spaces.txt'

run_parallel \
    'wc -c "$INPUT_FILE"' \
    'sha256sum "$INPUT_FILE"'
```

Ordinary unexported parent variables and arrays are not automatically available in child shells. Children inherit the working directory and exported environment. A child's `cd` or variable assignment does not change the parent or sibling shells.

### Build strings safely from dynamic arguments

Avoid inserting unquoted filenames or other data into executable shell strings. Bash's `printf %q` can encode individual arguments:

```bash
files=("first input.txt" "second input.txt")
commands=()

for file in "${files[@]}"; do
    printf -v command '%q ' wc -c -- "$file"
    commands+=("$command")
done

run_parallel "${commands[@]}" || exit "$?"
```

This preserves filenames as arguments even when they contain spaces or shell metacharacters. The function intentionally executes shell code, so command strings themselves must come from a trusted source.

## 9. Pipelines and output files

Enable `pipefail` inside a child when failure anywhere in its pipeline should fail the job:

```bash
run_parallel \
    'set -o pipefail; printf "hello\n" | wc -c' \
    'sleep 1 && echo "Other job"'
```

Without `pipefail`, a pipeline normally has the status of its last command, which can mask an earlier command's failure. With `pipefail`, Bash uses the rightmost nonzero pipeline status, or zero if all stages succeed.

To capture separate job logs:

```bash
mkdir -p logs

run_parallel \
    '(sleep 1 && echo A) > logs/a.log 2>&1' \
    '(sleep 2 && echo B) > logs/b.log 2>&1' \
    || exit "$?"
```

Parentheses group each sequence so its entire output is redirected. The outer function's starting and success messages still appear on its own standard output. The `>` operator overwrites each log; use `>>` to append. Avoid having independent jobs overwrite the same output file.

## 10. Use named functions for larger workflows

Export helper functions that child shells must call. Only `run_parallel` exports itself automatically.

```bash
group_a() {
    run_parallel \
        'sleep 2 && echo A1' \
        'sleep 1 && echo A2' \
        && echo "Group A follow-up"
}

group_b() {
    run_parallel \
        'sleep 1 && echo B1' \
        'sleep 2 && echo B2' \
        'sleep 3 && echo B3' \
        && echo "Group B follow-up"
}

export -f group_a group_b
run_parallel 'group_a' 'group_b' || exit "$?"
```

This reduces nested quoting and makes larger workflows easier to read. Export any additional functions or environment variables those helpers need.

## 11. Scope and limitations

- **No concurrency limit:** every command starts immediately. Large lists or nested groups can exhaust CPU, memory, file descriptors, or service capacity.
- **No timeouts or cancellation management:** the function installs no signal traps and does not explicitly terminate descendants. Its wait-for-all contract describes normal execution; signals or caller traps can interrupt waiting. It is not a process supervisor.
- **Foreground work within each job:** the function tracks the child shells it launches. A command string that starts detached background work and exits can return before that work finishes. Keep the actual job in the foreground or explicitly wait for its background children inside the command string.
- **Noninteractive jobs:** commands should not depend on shared terminal input. In a usual noninteractive Bash script, asynchronous jobs without explicit input redirection receive `/dev/null` as standard input.
- **Shared output:** concurrent text may interleave, including messages from nested groups. Use separate logs where needed.
- **Command visibility:** starting messages print the full command strings. Use environment variables or appropriate input files rather than embedding secrets in those strings.
- **Shell state:** the function does not install global shell options or traps, but calling it marks its definition for export. Child shells do not automatically inherit all parent shell settings or aliases.

For independent commands, prefer a flat list. Add groups when their own success boundaries or follow-up steps serve a purpose.
