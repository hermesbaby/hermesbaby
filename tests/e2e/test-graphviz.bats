#!/usr/bin/env bats

###############################################################################
# Local run (pwd is the repo's root):
#
# uv sync --all-groups
# source ./.venv/Scripts/activate
#
# tests/e2e/bats/bin/bats tests/e2e/test-graphviz.bats -x --show-output-of-passing-tests
###############################################################################

load "test_helper/load.bash"

setup_file() {
    TEST_DIR="tests/data/graphviz"
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

@test "hb text renders markdown with graphviz directive" {

    run python -m hermesbaby text
    assert_success

    assert_file_exist "out/docs/text/index.txt"

    # The graphviz directive must be known and rendered (the text builder
    # emits the alt text as placeholder, so no `dot` binary is needed).
    assert_file_contains "out/docs/text/index.txt" '\[graph: Simple flow\]'
    assert_file_contains "out/docs/text/index.txt" 'Text after the diagram.'

    # No complaint about an unknown directive
    assert_file_not_contains "out/docs/text/stderr.log" 'Unknown directive type'
}

@test "hb html renders markdown with graphviz directive as svg" {

    if ! command -v dot >/dev/null 2>&1; then
        skip "Graphviz 'dot' is not installed"
    fi

    run python -m hermesbaby html
    assert_success

    assert_file_exist "out/docs/html/index.html"
    assert_file_contains "out/docs/html/index.html" 'class="graphviz"'
    assert_file_contains "out/docs/html/index.html" '_images/graphviz-.*\.svg'
}
