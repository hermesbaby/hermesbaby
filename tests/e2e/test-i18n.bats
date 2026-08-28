#!/usr/bin/env bats

#########################################################################################
# Local run (pwd is the repo's root):
#
# source ./.venv/Scripts/activate
# tests/e2e/bats/bin/bats tests/e2e/test-i18n.bats -x --show-output-of-passing-tests
#########################################################################################

load "test_helper/load.bash"

setup_file() {
    TEST_DIR="tests/data/i18n"
    export TEST_DIR
    cd "$TEST_DIR"

    rm -rf docs/_locales
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

@test "hb i18n gettext: extracts .pot catalogs" {

    run python -m hermesbaby i18n gettext
    assert_success

    assert_file_exist "out/docs/gettext/index.pot"
}

@test "hb i18n update-po: creates .po catalogs for requested languages" {

    run python -m hermesbaby i18n update-po -l en -l de
    assert_success

    assert_file_exist "docs/_locales/en/LC_MESSAGES/index.po"
    assert_file_exist "docs/_locales/de/LC_MESSAGES/index.po"
}

@test "hb i18n update-po: preserves an existing translation on re-run" {

    # Fill in the (currently empty) msgstr for one specific msgid in place -
    # appending a duplicate msgid block would be invalid .po and silently
    # ignored by msgmerge/sphinx-intl; a blind msgstr replace would also
    # hit the other (still-untranslated) entry in this catalog.
    sed -i '/^msgid "This is a paragraph to translate\."$/{n;s/^msgstr ""$/msgstr "Dies ist ein Absatz zum Uebersetzen."/}' \
        docs/_locales/de/LC_MESSAGES/index.po
    run grep -F "Dies ist ein Absatz zum Uebersetzen." docs/_locales/de/LC_MESSAGES/index.po
    assert_success

    run python -m hermesbaby i18n update-po -l en -l de
    assert_success

    run grep -F "Dies ist ein Absatz zum Uebersetzen." docs/_locales/de/LC_MESSAGES/index.po
    assert_success
}

@test "hb i18n stats: reports raw per-catalog translation coverage" {

    run python -m hermesbaby i18n stats
    assert_success

    assert_output --partial "LC_MESSAGES"
    refute_output --partial "ALL"
}

@test "hb i18n stats-summary: reports aggregated translation coverage" {

    run python -m hermesbaby i18n stats-summary
    assert_success

    assert_output --partial "ALL"
}
