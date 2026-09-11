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
    :
}

setup() {
    :
}

teardown() {
    :
}

prepare_test_dir() {
    TEST_DIR="$1"
    cd "$TEST_DIR"

    rm -rf out_1/
    [ -d out ] && mv out out_1

    rm -rf out/

    export HERMES_PUBLISH_REPO='some-repo'
    export HERMES_API_TOKEN='some-token'
    export HERMES_PUBLISH_BASE_URL='some-base-url'
    export HERMES_PUBLISH_PROJECT='some-project'
    export HERMES_PUBLISH_BRANCH='some-branch'
    export HERMESBABY_CI_OPTIONS_JSON_PATH=build_parameters.json
    echo '{ "PUBLISH_SKIP_PUBLISH": "y" }' > $HERMESBABY_CI_OPTIONS_JSON_PATH
}

@test "a-no-languages" {

    TEST_DIR="tests/data/ci-i18n/a-no-languages"
    prepare_test_dir "$TEST_DIR"

    run python -m hermesbaby ci run
    assert_success

    # Challenge actual output against expectations

    assert_file_exist "out/docs/html.tar.gz"

    run tar -tzf out/docs/html.tar.gz
    assert_success
    assert_output --regexp $'(^|\n)\./?index\.html($|\n)' # Contains /index.html
}

@test "b-three-languages" {

    TEST_DIR="tests/data/ci-i18n/b-three-languages"
    prepare_test_dir "$TEST_DIR"

    run python -m hermesbaby ci run
    assert_success

    # Challenge actual output against expectations

    assert_file_exist "out/docs/html.tar.gz"

    run tar -tzf out/docs/html.tar.gz
    assert_success
    assert_output --regexp $'(^|\n)\./?fr/index\.html($|\n)' # Contains /fr/index.html
    assert_output --regexp $'(^|\n)\./?de/index\.html($|\n)' # Contains /de/index.html
    assert_output --regexp $'(^|\n)\./?en/index\.html($|\n)' # Contains /en/index.html
}

