#!/usr/bin/env bats

#########################################################################################
# Local run (pwd is the repo's root):
#
# bcomp tests/data/partly/out_1 tests/data/partly/out &
# source ./.venv/Scripts/activate
# tests/e2e/bats/bin/bats tests/e2e/test-partly.bats -x --show-output-of-passing-tests
#########################################################################################


load "test_helper/load.bash"

setup_file() {
    TEST_DIR="tests/data/partly"
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

    assert_file_contains "out/docs/text/glossary.txt" '^TermX'
    assert_file_contains "out/docs/text/glossary.txt" '^TermX'
    assert_file_contains "out/docs/text/glossary.txt" '^TermZ'

    assert_file_contains "out/docs/text/tree_a/index.txt" '.*'

    assert_file_contains "out/docs/text/tree_b/index.txt" ' \*TermX\*'
    assert_file_contains "out/docs/text/tree_b/index.txt" ' \*TermZ\*'

    assert_file_contains "out/docs/text/tree_c/index.txt" ' \*TermY\*'
    assert_file_contains "out/docs/text/tree_c/index.txt" ' \*TermZ\*'

    assert_file_contains "out/docs/text/tree_d/index.txt" 'The caption of the figure with Alice and Bob'

    assert_file_contains "out/docs/text/tree_e/index.txt" ' \*TermE\*'
    assert_file_contains "out/docs/text/tree_e/index.txt" ' \*TermZ\*'
}


@test "hb text --partly docs/tree_a" {

    run python -m hermesbaby text --partly docs/tree_a
    assert_success

    # Challenge actual output against expectations
    assert_file_exist "out/docs/text/index.txt"
    assert_file_contains "out/docs/text/index.txt" '.*'
}


@test "hb text --partly docs/tree_b" {

    run python -m hermesbaby text --partly docs/tree_b
    assert_success

    # Challenge actual output against expectations
    assert_file_exist "out/docs/text/index.txt"
    assert_file_contains "out/docs/text/index.txt" ' "TermX" used'
    assert_file_contains "out/docs/text/index.txt" ' "TermZ" used'
}

@test "hb text --partly docs/tree_c" {

    run python -m hermesbaby text --partly docs/tree_c
    assert_success

    # Challenge actual output against expectations
    assert_file_exist "out/docs/text/index.txt"
    assert_file_contains "out/docs/text/index.txt" ' "TermY" used'
    assert_file_contains "out/docs/text/index.txt" ' "TermZ" used'
}

@test "hb text --partly docs/tree_d" {

    run python -m hermesbaby text --partly docs/tree_d
    assert_success

    # Challenge actual output against expectations
    assert_file_exist "out/docs/text/index.txt"
    assert_file_contains "out/docs/text/index.txt" ' "fig_alice_and_bob" used'
}

@test "hb text --partly docs/tree_e" {

    run python -m hermesbaby text --partly docs/tree_e
    assert_success

    # Challenge actual output against expectations
    assert_file_exist "out/docs/text/index.txt"
    assert_file_not_contains "out/docs/text/index.txt" ' "TermE" used'
    assert_file_contains "out/docs/text/index.txt" ' "TermZ" used'
}

@test "hb text --partly docs/tree_f" {

    run python -m hermesbaby text --partly docs/tree_f
    #assert_success
    assert_failure

    # Challenge actual output against expectations
    #assert_file_exist "out/docs/text/index.txt"
    #assert_file_not_contains "out/docs/text/index.txt" ' "TermF" used'
    #assert_file_contains "out/docs/text/index.txt" ' "TermZ" used'
}

@test "hb html **" {

    run python -m hermesbaby html
    assert_success

    run python -m hermesbaby html --partly docs/tree_a
    assert_success

    run python -m hermesbaby html --partly docs/tree_b
    assert_success

    run python -m hermesbaby html --partly docs/tree_c
    assert_success

    run python -m hermesbaby html --partly docs/tree_d
    assert_success

    run python -m hermesbaby html --partly docs/tree_e
    assert_success

    run python -m hermesbaby html --partly docs/tree_f
    #assert_success
    assert_failure
}
