#!/usr/bin/env bats

#########################################################################################
# Local run (pwd is the repo's root):
#
# bcomp tests/data/htaccess/out_1 tests/data/htaccess/out &
# source ./.venv/Scripts/activate
# tests/e2e/bats/bin/bats tests/e2e/test-htaccess.bats -x --show-output-of-passing-tests
#########################################################################################

load "test_helper/load.bash"

setup_file() {
    TEST_DIR="tests/data/htaccess"
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

@test "hb html[-live]: Default htaccess is access to nobody" {

    # Check prerequisites
    assert_file_not_exists "./docs/htaccess.yaml"
    assert_file_not_exists "./docs/webroot/.htaccess"

    run python -m hermesbaby html
    assert_success

    # Challenge actual output against expectations

    assert_file_exist "out/docs/html/.htaccess"
}
