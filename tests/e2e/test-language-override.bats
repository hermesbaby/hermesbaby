#!/usr/bin/env bats

#########################################################################################
# Local run (pwd is the repo's root):
#
# source ./.venv/Scripts/activate
# tests/e2e/bats/bin/bats tests/e2e/test-language-override.bats -x --show-output-of-passing-tests
#########################################################################################

load "test_helper/load.bash"

setup_file() {
    TEST_DIR="tests/data/i18n"
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

@test "hb html: defaults to DOC__LANGUAGE (en)" {

    run python -m hermesbaby html
    assert_success

    run grep -o '<html[^>]*lang="[^"]*"' out/docs/html/index.html
    assert_success
    assert_output --partial 'lang="en"'
}

@test "hb html --language: overrides the build language without touching .hermesbaby" {

    assert_file_not_exists ".hermesbaby"

    run python -m hermesbaby html -l de
    assert_success

    run grep -o '<html[^>]*lang="[^"]*"' out/docs/html/index.html
    assert_success
    assert_output --partial 'lang="de"'

    assert_file_not_exists ".hermesbaby"
}
