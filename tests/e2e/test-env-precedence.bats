#!/usr/bin/env bats

load "test_helper/load.bash"

setup_file() {
    TEST_DIR="$(mktemp -d)"
    export TEST_DIR
    cd "$TEST_DIR"
}

teardown_file() {
    rm -rf "$TEST_DIR"
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
