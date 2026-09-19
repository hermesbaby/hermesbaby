#!/usr/bin/env bats

#########################################################################################
# Local run (pwd is the repo's root):
#
# source ./.venv/Scripts/activate
# tests/e2e/bats/bin/bats tests/e2e/test-filebased-toctree-order.bats -x --show-output-of-passing-tests
#########################################################################################
#
# These tests verify that "filesystem" toctree mode reflects the source tree
# correctly: index.md is always the parent/first document, siblings sort
# alphabetically with numeric-aware (leading-zero-safe) ordering, folder
# hierarchy is preserved depth-first, and a folder with no files of its own
# (only subfolders) is dropped rather than crashing the build.
#
# Each fixture is built with "hb html", and the resulting reading order is
# reconstructed by following the rel="next" links Sphinx writes into every
# page's <head> (see test_helper/extract_doc_order.py), then compared
# against a recorded expected/order.txt.
#########################################################################################

load "test_helper/load.bash"

EXTRACT_ORDER="${BATS_TEST_DIRNAME}/test_helper/extract_doc_order.py"

setup_file() {
    TEST_DIR="tests/data/filebased-toctree"
    export TEST_DIR
    cd "$TEST_DIR"
}

setup() {
    :
}

teardown() {
    :
}

assert_doc_order() {
    local fixture="$1"

    cd "$fixture"
    rm -rf out

    run python -m hermesbaby html
    assert_success

    python3 "$EXTRACT_ORDER" out/docs/html > out/order.txt
    assert_files_equal_ignore_eol out/order.txt expected/order.txt

    cd ..
}

# A project with only a root document: the minimal document tree.
@test "d-single-file" {
    assert_doc_order d-single-file
}

# A flat set of siblings: alphabetical sort, numeric-aware sort (including
# leading zeros, e.g. "01" before "2" before "10"), a mix of both in the same
# folder, and index.md always coming first even though another file's name
# ("aaa-alphabetically-first") would otherwise sort before it.
@test "e-flat-order" {
    assert_doc_order e-flat-order
}

# Folder hierarchy: a plain sibling file and a numerically-earlier-named
# subfolder at the same level (files always come before subfolders,
# regardless of name), a two-level-deep nested folder, and depth-first
# traversal (a folder's own children are visited before its next sibling).
@test "f-hierarchy" {
    assert_doc_order f-hierarchy
}

# A folder containing only a subfolder (no files of its own): sphinx-etoc
# never descends into it, so the whole subtree -- including real content
# further down -- is dropped from the generated document tree. The dropped
# pages are marked "orphan: true" so the build doesn't fail on Sphinx's
# "not included in any toctree" warning.
@test "g-folder-without-files" {
    assert_doc_order g-folder-without-files
}
