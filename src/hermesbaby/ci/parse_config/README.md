<!---
################################################################
#                                                              #
#  This file is part of HermesBaby                             #
#                       the software engineer's typewriter     #
#                                                              #
#      https://github.com/hermesbaby                           #
#                                                              #
#  Copyright (c) 2024 Alexander Mann-Wahrenberg (basejumpa)    #
#                                                              #
#  License(s)                                                  #
#                                                              #
#  - MIT for contents used as software                         #
#  - CC BY-SA-4.0 for contents used as method or otherwise     #
#                                                              #
################################################################
-->

# User Guide: parse_config.py

`parse_config.py` is a command-line utility that converts JSON configuration files into shell environment variable exports.

## Usage

### Command Line

```bash
python parse_config.py <file-path>
```

Or run it as a module:

```bash
python -m parse_config <file-path>
```

To actually set the environment variables in your current shell session, use `eval`:

```bash
eval $(python parse_config.py config.json)
```

### Python Module

You can also import the functionality into your own Python scripts:

```python
from parse_config import get_env_vars_from_json, format_as_export_commands

env_vars = get_env_vars_from_json("config.json")
commands = format_as_export_commands(env_vars)
for cmd in commands:
    print(cmd)
```

## Features

- **Environment Exports**: Generates `export HERMESBABY_CI__KEY="VALUE"` statements for each key in the JSON.
- **Prefixing**: All environment variables are prefixed with `HERMESBABY_CI__`.
- **Flattening**: Nested JSON objects are flattened using double underscores (`__`) as separators (e.g., `{"database": {"host": "localhost"}}` becomes `HERMESBABY_CI__DATABASE__HOST="localhost"`).
- **Normalization**: Keys are automatically converted to uppercase, and hyphens are replaced with underscores.
- **JSON Validation**: Ensures the file contains valid JSON before processing.
- **Error Handling**:
  - Reports missing files, directories, or invalid JSON to `stderr`.
  - Displays a usage message if no file path is provided.

## Exit Codes

- `0`: Success.
- `1`: Error (file not found, invalid JSON, path is a directory, or missing arguments).

## Contribution Guide

We follow a **Test-Driven Development (TDD)** approach for extending or modifying this utility.

### Development Workflow

1. **Create a Reproducing Test**: Before making any changes, add a new test case to `test.py` that describes the desired behavior or reproduces a bug.
2. **Run Tests (Red)**: Execute the tests to confirm that the new test fails.

    ```bash
    pytest test.py
    ```

3. **Implement Changes**: Modify `parse_config.py` to implement the new feature or fix the bug.
4. **Verify (Green)**: Run the tests again to ensure all tests (including the new one) pass.
5. **Refactor**: Clean up the code if necessary, ensuring tests remain green.

### Adding New Tests

When adding tests, prefer using the `tmp_path` fixture provided by `pytest` to create temporary JSON files. Ensure you test:

- Valid JSON input.
- Edge cases (empty objects, deeply nested structures).
- Invalid inputs (malformed JSON, non-existent files).
- Shell-specific characters (to ensure proper escaping).
