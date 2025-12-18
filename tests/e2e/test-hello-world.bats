#!/usr/bin/env bats

# This is a simple BATS test file to serve as a starting point for E2E tests.
# BATS (Bash Automated Testing System) is a TAP-compliant testing framework for Bash.

setup() {
    # This function runs before each test.
    # Create a temporary directory for the test to avoid polluting the workspace.
    TEST_DIR="$(mktemp -d)"
    export TEST_DIR
    cd "$TEST_DIR"
}

teardown() {
    # This function runs after each test.
    # Clean up the temporary directory.
    rm -rf "$TEST_DIR"
}

@test "Check something" {
    # This is a sample test case.
    # You can replace this with actual test logic.

    run echo "Hello World"

    # Check if the output is as expected.
    [ "$output" = "Hello World" ]

    # [ "$status" -eq 0 ] checks if the command succeeded.
    [ "$status" -eq 0 ]
}
