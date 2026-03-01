#!/usr/bin/env bats

#################################################################################
# Local run (pwd is the repo's root):
#
# tests/e2e/bats/bin/bats tests/e2e/test-new.bats -x --show-output-of-passing-tests
#
#################################################################################



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
    rm -rf "out/"
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

@test "hb new" {

    assert_file_not_exists "docs/index.md"
    run python -m hermesbaby new --template zero
    assert_success
    assert_file_exist "docs/index.md"

    assert_file_exist "docs/index.md"
    run python -m hermesbaby new --template hello
    assert_failure
    assert_file_contains "docs/index.md" '# Zero'

    assert_file_exist "docs/index.md"
    run python -m hermesbaby new --template hello --force
    assert_success
    assert_file_contains "docs/index.md" '# Hello'

}
