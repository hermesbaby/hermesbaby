#!/usr/bin/env bats

setup_file() {
    # Get the project root
    PROJECT_ROOT="$(cd "$(dirname "$BATS_TEST_FILENAME")/../.." >/dev/null 2>&1 && pwd)"
    export PROJECT_ROOT
    echo "PROJECT_ROOT: $PROJECT_ROOT" >&3

    # Activate virtualenv and get templates
    source "$PROJECT_ROOT/.venv/Scripts/activate"

    TEMPLATES_PRIORITY="zero hello log-ledger"
    ALL_TEMPLATES=$(python -m hermesbaby new --list-templates | grep -E ' - ' | sed 's/ *- //g')
    echo "ALL_TEMPLATES: $ALL_TEMPLATES" >&3

    # Ensure priority templates are first and unique
    TEMPLATES=$(echo "$TEMPLATES_PRIORITY $ALL_TEMPLATES" | tr ' ' '\n' | awk '!seen[$0]++' | tr '\n' ' ')
    export TEMPLATES
    export COMMANDS="html pdf"
}

setup() {
    # Create a temporary directory for each test
    TEST_DIR="$(mktemp -d)"
    export TEST_DIR
    cd "$TEST_DIR"

    # Ensure we are using the project's hermesbaby
    source "$PROJECT_ROOT/.venv/Scripts/activate"
}

teardown() {
    rm -rf "$TEST_DIR"
}

@test "All templates can be initialized and built" {
    for template in $TEMPLATES; do
        echo "Testing template: $template" >&3

        # Create a new project directory for this template
        template_dir="$TEST_DIR/$template"
        mkdir -p "$template_dir"

        run python -m hermesbaby new --template "$template" "$template_dir"
        [ "$status" -eq 0 ]

        cd "$template_dir"

        # Special case for log-ledger
        if [ "$template" = "log-ledger" ]; then
            run ./mk-my-day.sh --skip-open-vscode
            [ "$status" -eq 0 ]
        fi

        # Run build commands
        for command in $COMMANDS; do
            echo "  Building command: $command" >&3
            run python -m hermesbaby "$command"
            [ "$status" -eq 0 ]
        done

        cd "$TEST_DIR"
    done
}
