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

@test "alex hb html --language: overrides the build language without touching .hermesbaby" {

    assert_file_not_exists ".hermesbaby"

    run python -m hermesbaby html -l de
    assert_success

    run grep -o '<html[^>]*lang="[^"]*"' out/docs/html/de/index.html
    assert_success
    assert_output --partial 'lang="de"'

    assert_file_not_exists ".hermesbaby"
}


@test " hb text [--language de|fr]" {

    rm -rf out/docs
    run hb text
    assert_file_exists out/docs/text/index.txt

    rm -rf out/docs
    run hb text --language de
    assert_file_exists out/docs/text/de/index.txt

    rm -rf out/docs
    run hb text --language fr
    assert_file_exists out/docs/text/fr/index.txt
}

@test "hb html [--language en|fr_CI]" {

    rm -rf out/docs
    run hb html
    assert_file_exists out/docs/html/index.html

    rm -rf out/docs
    run hb html --language en
    assert_file_exists out/docs/html/en/index.html

    rm -rf out/docs
    run hb html --language fr_CI
    assert_file_exists out/docs/html/fr_CI/index.html
}

@test "hb pdf [--language de|es]" {

    rm -rf out/docs
    run hb pdf
    assert_file_exists out/docs/pdf/the_default_title.pdf

    rm -rf out/docs
    run hb pdf --language de
    assert_file_exists out/docs/pdf/de/the_default_title.pdf

    rm -rf out/docs
    run hb pdf --language es
    assert_file_exists out/docs/pdf/es/the_default_title.pdf
}
