#!/usr/bin/env bats

load "test_helper/load.bash"

setup_file() {
    PROJECT_ROOT="$(cd "$(dirname "$BATS_TEST_FILENAME")/../.." >/dev/null 2>&1 && pwd)"
    export PROJECT_ROOT

    TEST_DIR="$(mktemp -d)"
    TOOL_DIR="$(mktemp -d)"
    export TEST_DIR
    cd "$TEST_DIR"

    cat > "$TOOL_DIR/hb" <<'EOF'
#!/usr/bin/env bash
python -m hermesbaby "$@"
EOF
    chmod +x "$TOOL_DIR/hb"
    export PATH="$TOOL_DIR:$PATH"
    export PYTHONPATH="$PROJECT_ROOT/src${PYTHONPATH:+:$PYTHONPATH}"
}

teardown_file() {
    rm -rf "$TEST_DIR"
    rm -rf "$TOOL_DIR"
}

@test "CONFIG_* environment variables override .hermesbaby for hb text" {
    run hb new -t zero
    assert_success

    cat > .hermesbaby <<'EOF'
CONFIG_BUILD__DIRS__BUILD="from-file-out"
EOF

    export CONFIG_BUILD__DIRS__BUILD="from-env-out"

    run hb text
    assert_success

    assert_file_exist "from-env-out/text/index.txt"
    assert_file_not_exist "from-file-out/text/index.txt"
}
