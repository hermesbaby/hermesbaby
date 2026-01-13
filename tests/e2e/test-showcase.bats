#!/usr/bin/env bats

setup() {
    TEST_DIR="tests/data/showcases"
    export TEST_DIR
    cd "$TEST_DIR"

    rm -f .hermesbaby
    python -m hermesbaby configure --update

    rm -rf out/
}

teardown() {
    :
}

_configure_subtree() {
    subtree="$1"

    sed -i "s/\(CONFIG_DOC__TITLE\)=.*/\1=\"$subtree\"/" .hermesbaby
    sed -i "s/\(CONFIG_BUILD__DIRS__SOURCE\)=.*/\1=\"$subtree\"/" .hermesbaby
    sed -i "s/\(CONFIG_BUILD__DIRS__CONFIG\)=.*/\1=\"$subtree\"/" .hermesbaby
    sed -i "s/\(CONFIG_BUILD__DIRS__BUILD\)=.*/\1=\"out\/subtrees\/$subtree\"/" .hermesbaby
}

@test "hb html --subtree drawio)" {

    subtree="drawio"

    _configure_subtree "$subtree"

    run python -m hermesbaby html
    [ "$status" -eq 0 ]
}

@test "hb html --subtree tables)" {

    subtree="tables"

    _configure_subtree "$subtree"

    run python -m hermesbaby html
    [ "$status" -eq 0 ]
}

@test "hb pdf --subtree drawio)" {

    subtree="drawio"

    _configure_subtree "$subtree"

    run python -m hermesbaby pdf
    [ "$status" -eq 0 ]
}

@test "hb pdf --subtree tables)" {

    subtree="tables"

    _configure_subtree "$subtree"

    run python -m hermesbaby pdf
    [ "$status" -eq 0 ]
}
