#!/usr/bin/env bats

setup() {
    # Get the project root (assuming this script is in tests/e2e/)
    PROJECT_ROOT="$(cd "$(dirname "$BATS_TEST_FILENAME")/../.." >/dev/null 2>&1 && pwd)"
    export PROJECT_ROOT

    # Create a temporary directory for the test
    TEST_DIR="$(mktemp -d)"
    export TEST_DIR
    cd "$TEST_DIR"
}

teardown() {
    rm -rf "$TEST_DIR"
}

@test "CI can create and embed PDF into HTML package" {
    # Activate virtualenv
    # Use the absolute path from the original script as a fallback if PROJECT_ROOT is tricky,
    # but PROJECT_ROOT should work.
    source "$PROJECT_ROOT/.venv/Scripts/activate"

    # Create test data
    run python -m hermesbaby new --template hello .
    [ "$status" -eq 0 ]

    git init .
    git add .
    git commit -m "1"
    echo '{ "PUBLISH__CREATE_AND_EMBED_PDF": "y" }' > build_parameters.json
    export CONFIG_PUBLISH_SKIP_PUBLISH="y"

    # Item-under-test:
    run "$PROJECT_ROOT/src/hermesbaby/ci/run.sh"
    [ "$status" -eq 0 ]

    # Evaluate
    [ -f "./out/docs/html.tar.gz" ]

    run tar -tzf ./out/docs/html.tar.gz
    [ "$status" -eq 0 ]
    echo "$output" | grep "the_default_title.pdf"
}
