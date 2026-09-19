#!/usr/bin/env bats

#########################################################################################
# Local run (pwd is the repo's root):
#
# bcomp tests/data/template/out_1 tests/data/template/out &
# source ./.venv/Scripts/activate
# tests/e2e/bats/bin/bats tests/e2e/test-template.bats -x --show-output-of-passing-tests
#########################################################################################

load "test_helper/load.bash"

setup_file() {
    TEST_DIR="tests/data/filebased-toctree"
    export TEST_DIR
    cd "$TEST_DIR"

    rm -rf "$TEST_DIR/out"
}

setup() {
    :
}

teardown() {
    # This function runs after each test.
    # Clean up the temporary directory.
    # Add any additional teardown steps here if necessary.
    # For now we just leave it empty and place a no-op:
    :
}

@test "a" {

    cd a-directive
    run python -m hermesbaby text
    assert_success
    assert_files_equal_ignore_eol "out/docs/text/index.txt" expected/index.txt

    cd ../a-filesystem
    run python -m hermesbaby text
    assert_success
    assert_files_equal_ignore_eol "out/docs/text/index.txt" expected/index.txt

    cd ..
}

# Covers the "toctree" frontmatter block on a flat set of siblings: absent,
# unrelated (no "toctree" key), null, title-only, options-only (all
# sphinx-external-toc options combined on the root), non-bool/non-str option
# values (numbered as int, style as a list), and an attempt to inject
# structural keys ("root"/"entries") via frontmatter, which must be stripped.
@test "b-options" {

    cd b-options
    run python -m hermesbaby text
    assert_success
    assert_files_equal_ignore_eol "out/docs/text/_toc.yml" expected/_toc.yml

    cd ..
}

# Covers filesystem topology: nested folders (depth 1 and depth 2) each
# carrying their own "toctree" options without leaking into siblings or
# ancestors, a folder whose index file isn't literally named "index"
# (natural-sort fallback), and a folder containing only a subfolder (no
# files directly inside it), which sphinx-etoc silently drops from the
# generated _toc.yml.
@test "c-nesting" {

    cd c-nesting
    run python -m hermesbaby text
    assert_success
    assert_files_equal_ignore_eol "out/docs/text/_toc.yml" expected/_toc.yml

    cd ..
}

# With "filesystem" toctree mode active, a source file may still contain an
# explicit ```{toctree}``` directive (i.e. "directive" mode syntax), e.g.
# left over from a copy-paste. Since the document hierarchy is derived from
# _toc.yml, such a directive is redundant. It must be tolerated and
# neglected (silently dropped) rather than making sphinx-external-toc raise
# "toctree directive not expected with external-toc" [etoc.toctree], which
# hermesbaby's default -W (warn-as-error) build would otherwise turn into a
# hard failure.
@test "h-explicit-toctree-directive" {

    cd h-explicit-toctree-directive
    run python -m hermesbaby html
    assert_success
    refute_output --partial "toctree directive not expected with external-toc"
    refute_output --partial "etoc.toctree"

    cd ..
}

# conf.py's exclude_patterns excludes a downward-compatibility README.md and
# the _attachments/_listings/_unused folders from the Sphinx build.
# sphinx-etoc doesn't know about exclude_patterns, so it would otherwise add
# those to _toc.yml, and Sphinx would then fail with "toctree contains
# reference to nonexisting document" once warnings are treated as errors.
# This verifies they're pruned instead, alongside a normal, non-excluded
# folder that must still come through untouched.
@test "i-exclude-patterns" {

    cd i-exclude-patterns
    run python -m hermesbaby html
    assert_success
    assert_files_equal_ignore_eol "out/docs/html/_toc.yml" expected/_toc.yml

    python3 "${BATS_TEST_DIRNAME}/test_helper/extract_doc_order.py" out/docs/html > out/order.txt
    assert_files_equal_ignore_eol out/order.txt expected/order.txt

    cd ..
}
