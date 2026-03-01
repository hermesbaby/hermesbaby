#!/usr/bin/env bats

#########################################################################################
# Local run (pwd is the repo's root):
#
# bcomp tests/data/template/out_1 tests/data/template/out &
# source ./.venv/Scripts/activate
# tests/e2e/bats/bin/bats tests/e2e/test-template.bats -x --show-output-of-passing-tests
#########################################################################################

load "test_helper/load.bash"

setup_file() {
    TEST_DIR="tests/data/template"
    export TEST_DIR
    cd "$TEST_DIR"

    rm -rf out_1/
    [ -d out ] && mv out out_1

    rm -rf out/
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

@test "hb text" {

    run python -m hermesbaby text
    assert_success

    # Challenge actual output against expectations

    assert_file_exist "out/docs/text/console.log"
    assert_file_exist "out/docs/text/stdout.log"
    assert_file_exist "out/docs/text/stderr.log"

    assert_file_exist "out/docs/text/index.txt"
}
