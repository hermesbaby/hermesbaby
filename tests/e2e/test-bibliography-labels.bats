#!/usr/bin/env bats

###############################################################################
# Local run (pwd is the repo's root):
#
# source ./.venv/Scripts/activate
# tests/e2e/bats/bin/bats tests/e2e/test-bibliography-labels.bats -x --show-output-of-passing-tests
###############################################################################

load "test_helper/load.bash"

setup_file() {
    TEST_DIR="tests/data/bibliography-labels"
    export TEST_DIR
    cd "$TEST_DIR"

    rm -rf out/
}

setup() {
    :
}

teardown() {
    :
}

@test "hb text: label/shorthand override the citation label" {

    run python -m hermesbaby text
    assert_success

    assert_file_exist "out/docs/text/index.txt"
    F="out/docs/text/index.txt"

    # No override: generated Author+Year label (unchanged behavior)
    assert_file_contains "$F" '\[Tri26\]'
    assert_file_contains "$F" 'Plain entry'
    assert_file_contains "$F" '\[Smi64\]'
    assert_file_contains "$F" 'Book Plain'

    # label / shorthand
    assert_file_contains "$F" '\[SLA_label\]'
    assert_file_contains "$F" 'Entry with label\.'
    assert_file_contains "$F" '\[SLA_shorthand\]'
    assert_file_contains "$F" 'Entry with shorthand'

    # label wins over shorthand
    assert_file_contains "$F" '\[BOTH_label\]'
    assert_file_not_contains "$F" 'BOTH_shorthand'

    # empty label falls back to the generated one
    assert_file_contains "$F" '\[Emp26\]'
    assert_file_contains "$F" 'Entry with empty label'

    # existing 'key' behavior for misc remains; label beats key
    assert_file_contains "$F" '\[KEY_only\]'
    assert_file_contains "$F" '\[LABEL_beats_key\]'
    assert_file_not_contains "$F" 'KEY_ignored'

    # works for other entry types
    assert_file_contains "$F" '\[BOOK_label\]'
    assert_file_contains "$F" 'Book With Label'
}
