#!/usr/bin/env bats

setup_file() {
    # Get the project root
    PROJECT_ROOT="$(cd "$(dirname "$BATS_TEST_FILENAME")/../.." >/dev/null 2>&1 && pwd)"
    export PROJECT_ROOT
}

setup() {
    # Create a temporary directory for each test
    TEST_DIR="$(mktemp -d)"
    export TEST_DIR
    cd "$TEST_DIR"
}

teardown() {
    rm -rf "$TEST_DIR"
}

build_template() {
    local template="$1"

    # Create a new project directory for this template
    run python3 -m hermesbaby new --template "$template" .
    [ "$status" -eq 0 ]

    # Special case for log-ledger
    if [ "$template" = "log-ledger" ]; then
        chmod +x ./mk-my-day.sh
        run ./mk-my-day.sh --skip-open-vscode
        [ "$status" -eq 0 ]
    fi

    # Run build commands
    run python -m hermesbaby html
    [ "$status" -eq 0 ]

    # run python -m hermesbaby pdf
    # [ "$status" -eq 0 ]
}

@test "Template: zero" {
    build_template "zero"
}

@test "Template: hello" {
    build_template "hello"
}

@test "Template: log-ledger" {
    build_template "log-ledger"
}

@test "Template: arc42-de" {
    build_template "arc42-de"
}

@test "Template: arc42-en" {
    build_template "arc42-en"
}
