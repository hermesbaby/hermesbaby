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

    # Inline diagrams are rendered as images, not shown as XML code listings
    html_dir=$(find out/subtrees/drawio -name index.html -path "*html*" | head -n 1)
    [ -n "$html_dir" ]
    ! grep -q "&lt;mxfile" "$html_dir"
    grep -q "drawio" "$html_dir"
    # No intermediate .drawio files are generated in the source tree
    [ -z "$(git ls-files --others --exclude-standard tests/data/showcases/drawio | grep '\.drawio$')" ]
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
