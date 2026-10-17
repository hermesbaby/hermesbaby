#!/usr/bin/env bats

#########################################################################################
# Local run (pwd is the repo's root):
#
# bcomp tests/data/partly-two/out_1 tests/data/partly-two/out &
# source ./.venv/Scripts/activate
# tests/e2e/bats/bin/bats tests/e2e/test-partly-two.bats -x --show-output-of-passing-tests
#########################################################################################


load "test_helper/load.bash"

setup_file() {
    TEST_DIR="tests/data/partly-two"
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
    assert_file_exist "out/docs/text/index.txt"
}

@test "hb html" {

    run python -m hermesbaby html
    assert_success

    # Challenge actual output against expectations
    assert_file_exist "out/docs/html/index.html"
}

@test "hb text --partly docs/SomeSystem" {

    run python -m hermesbaby text --partly docs/SomeSystem
    assert_success

    # Challenge actual output against expectations
    assert_file_exist "out/docs/text/index.txt"
}

@test "hb text --partly docs/SomeSystem/named-entry/named-entry.md" {

    run python -m hermesbaby text --partly docs/SomeSystem/named-entry/named-entry.md
    assert_success

    assert_file_exist "out/docs/text/named-entry.txt"
    assert_file_contains "out/docs/text/named-entry.txt" "Markdown named entry point"
}

@test "hb text --partly docs/SomeSystem/other-entry/other-entry.rst" {

    run python -m hermesbaby text --partly "$PWD/docs/SomeSystem/other-entry/other-entry.rst"
    assert_success

    assert_file_exist "out/docs/text/other-entry.txt"
    assert_file_contains "out/docs/text/other-entry.txt" "reStructuredText named entry point"
}

@test "cd docs/SomeSystem && hb text --partly ." {

    cd docs/SomeSystem
    run python -m hermesbaby text --partly .
    assert_success
    cd ../..

    # Challenge actual output against expectations
    assert_file_exist "out/docs/text/index.txt"
}

@test "cd docs/SomeSystem && hb html --partly ." {

    cd docs/SomeSystem
    run python -m hermesbaby html --partly .
    assert_success
    cd ../..

    # Challenge actual output against expectations
    assert_file_exist "out/docs/html/index.html"
}
