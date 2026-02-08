#!/usr/bin/env bats

# This is a simple BATS test file to serve as a starting point for E2E tests.
# BATS (Bash Automated Testing System) is a TAP-compliant testing framework for Bash.

## Bats documentation and tutorial and the codebase of BATS
# - @see https://bats-core.readthedocs.io/en/stable/
# - @see https://bats-core.readthedocs.io/en/stable/tutorial.html
# - @see https://github.com/bats-core/bats-core

load "test_helper/load.bash"

setup_file() {
    # This function runs before each test.
    # Create a temporary directory for the test to avoid polluting the workspace.
    TEST_DIR="$(mktemp -d)"
    export TEST_DIR
    cd "$TEST_DIR"

    # Keep previous run in mind to enable diffing while developing
    # rm -rf out_1/
    # cp -r out/ out_1/

    # Clean up any previous output directories if they exist.
    rm -rf "$TEST_DIR"
}

setup() {
    :
}

teardown() {
    # This function runs after each test.
    # Clean up the temporary directory.
    # Add any additional teardown steps here if necessary.
    # For now we just leave it empty and place a no-op:
    :
}

@test "Check something" {
    # This is a sample test case.
    # You can replace this with actual test logic.

    run echo "Hello World"

    # [ "$status" -eq 0 ] checks if the command succeeded.
    [ "$status" -eq 0 ]

    # Check if the output is as expected.
    output="Hello World"
    [ "$output" = "Hello World" ]

}
