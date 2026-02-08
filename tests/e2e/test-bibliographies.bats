#!/usr/bin/env bats

###############################################################################
# Local run (pwd is the repo's root):
#
# poetry install --with dev
# source ./.venv/Scripts/activate
#
# tests/e2e/bats/bin/bats tests/e2e/test-bibliographies.bats -x --show-output-of-passing-tests
#
# After the 2nd run, you can compare the outputs with:
#
# bcomp tests/data/bibliographies/out_1 tests/data/bibliographies/out &
###############################################################################


load "test_helper/load.bash"

setup_file() {
    TEST_DIR="tests/data/bibliographies"
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

    assert_file_contains "out/docs/text/index.txt" '\[Smi64\]'
    assert_file_contains "out/docs/text/index.txt" 'When the Lion Feeds'
    assert_file_contains "out/docs/text/index.txt" '\[Smi66\]'
    assert_file_contains "out/docs/text/index.txt" 'The Sound of Thunder'
    assert_file_contains "out/docs/text/index.txt" '\[Smi93\]'
    assert_file_contains "out/docs/text/index.txt" 'River God'

    assert_file_contains "out/docs/text/index.txt" '\[basejumpa25\]'
    assert_file_contains "out/docs/text/index.txt" 'Alexander Mann-Wahrenberg (basejumpa). «article»'

    assert_file_contains "out/docs/text/index.txt" '\[Mic24\]'
    assert_file_contains "out/docs/text/index.txt" 'Microsoft. Maintain an architecture decision record (adr).'

    assert_file_not_contains "out/docs/text/index.txt" '\[Lei17\]'
    assert_file_not_contains "out/docs/text/index.txt" 'Barry Leiba. Ambiguity of uppercase vs lowercase in rfc 2119'
}

