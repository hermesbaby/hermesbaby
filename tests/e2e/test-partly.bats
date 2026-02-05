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

    assert_file_exist "out/docs/text/index.txt"
}
