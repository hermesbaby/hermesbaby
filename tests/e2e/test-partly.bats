#!/usr/bin/env bats

load "test_helper/load.bash"

setup() {
    TEST_DIR="tests/data/partly"
    export TEST_DIR
    cd "$TEST_DIR"

    rm -rf out_1/
    cp -r out/ out_1/

    rm -rf out/
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
}


@test "hb text --partly docs/tree_a" {

    run python -m hermesbaby text --partly docs/tree_a
    assert_success

    # Challenge actual output against expectations
    assert_file_exist "out/docs/text/index.txt"
}


# @test "hb text --partly docs/tree_b" {
#
#     run python -m hermesbaby text --partly docs/tree_a
#     assert_success
#
#     # Challenge actual output against expectations
#
#     assert_file_exist "out/docs/text/index.txt"
# }

# @test "hb text --partly docs/tree_c" {
#
#     run python -m hermesbaby text --partly docs/tree_c
#     assert_success
#
#     # Challenge actual output against expectations
#
#     assert_file_exist "out/docs/text/index.txt"
# }
