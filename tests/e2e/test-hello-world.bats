#!/usr/bin/env bats

# This is a simple BATS test file to serve as a starting point for E2E tests.
# BATS (Bash Automated Testing System) is a TAP-compliant testing framework for Bash.

## Bats documentation and tutorial
# - @see https://bats-core.readthedocs.io/en/stable/?utm_source=chatgpt.com
# - @see https://bats-core.readthedocs.io/en/stable/tutorial.html?utm_source=chatgpt.com

setup() {
    # This function runs before each test.
    # Create a temporary directory for the test to avoid polluting the workspace.
    TEST_DIR="$(mktemp -d)"
    export TEST_DIR
    cd "$TEST_DIR"

    # Keep previous run in mind to enable diffing while developing
    rm -rf out_1/
    cp -r out/ out_1/

    # Clean up any previous output directories if they exist.
    rm -rf "$TEST_DIR"
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
    output = "Hello World"
    [ "$output" = "Hello World" ]

}
