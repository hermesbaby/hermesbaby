#!/usr/bin/env bats

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
    [ "$status" -eq 0 ]

    # Challenge actual output against expectations

    # There shall be the document's entry
    [ -f out/docs/text/index.txt ]

}
