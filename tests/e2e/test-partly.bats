#!/usr/bin/env bats

setup() {
    TEST_DIR="tests/data/partly"
    export TEST_DIR
    cd "$TEST_DIR"

    rm -rf out/
}

teardown() {
    :
}

@test "hb html" {

    run python -m hermesbaby html
    [ "$status" -eq 0 ]

    output="Hello World"
    [ "$output" = "Hello World" ]

}
