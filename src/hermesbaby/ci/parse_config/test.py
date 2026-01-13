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

import subprocess
import os
import pytest
import sys

# Add current directory to sys.path to allow importing parse_config
sys.path.append(os.path.dirname(__file__))
import parse_config

# Path to the script to be tested
SCRIPT_PATH = os.path.join(os.path.dirname(__file__), "parse_config.py")

def run_script(args):
    """Helper to run the script and return its output and exit code."""
    result = subprocess.run(
        [sys.executable, SCRIPT_PATH] + args,
        capture_output=True,
        text=True
    )
    return result

def test_valid_json_file(tmp_path):
    """Test script with a valid JSON file."""
    test_file = tmp_path / "test.json"
    content = '{"key": "value", "number": 123, "nested": {"a": "b"}, "special": "$\\\\`\\""}'
    test_file.write_text(content)

    result = run_script([str(test_file)])

    assert result.returncode == 0
    assert 'export CONFIG_KEY="value"' in result.stdout
    assert 'export CONFIG_NUMBER="123"' in result.stdout
    assert 'export CONFIG_NESTED__A="b"' in result.stdout
    assert 'export CONFIG_SPECIAL="\\$\\\\\\`\\""' in result.stdout
    assert result.stderr == ""

def test_module_usage(tmp_path):
    """Test using the script as a Python module."""
    test_file = tmp_path / "module_test.json"
    test_file.write_text('{"key": "value", "nested": {"a": 1}}')

    env_vars = parse_config.get_env_vars_from_json(str(test_file), prefix="TEST_")

    assert env_vars["TEST_KEY"] == "value"
    assert env_vars["TEST_NESTED__A"] == "1"

    commands = parse_config.format_as_export_commands(env_vars)
    assert 'export TEST_KEY="value"' in commands
    assert 'export TEST_NESTED__A="1"' in commands

def test_shell_integration(tmp_path):
    """Test that the output can be eval'd by a shell to set variables."""
    if os.name == 'nt':
        # On Windows, we'd need a bash-like shell (like git bash) to test 'eval' and 'export'
        # Skipping for now or using a simplified check if possible.
        pytest.skip("Shell integration test requires a POSIX-compliant shell (bash/sh)")

    test_file = tmp_path / "test.json"
    test_file.write_text('{"MY_VAR": "my_value"}')

    # Run the script and eval its output in a bash shell
    cmd = f'eval $({sys.executable} {SCRIPT_PATH} {test_file}) && echo $CONFIG_MY_VAR'
    result = subprocess.run(['bash', '-c', cmd], capture_output=True, text=True)

    assert result.returncode == 0
    assert result.stdout.strip() == "my_value"

def test_non_dict_json(tmp_path):
    """Test script with a JSON that is not a dictionary at top level."""
    test_file = tmp_path / "list.json"
    test_file.write_text('[1, 2, 3]')

    result = run_script([str(test_file)])

    assert result.returncode == 1
    assert "must contain a JSON object" in result.stderr

def test_invalid_json_file(tmp_path):
    """Test script with an invalid JSON file."""
    test_file = tmp_path / "invalid.json"
    content = "This is not JSON"
    test_file.write_text(content)

    result = run_script([str(test_file)])

    assert result.returncode == 1
    assert "is not a valid JSON file" in result.stderr
    assert result.stdout == ""

def test_non_existing_file():
    """Test script with a non-existing file."""
    result = run_script(["non_existent_file.txt"])

    assert result.returncode == 1
    assert "does not exist" in result.stderr
    assert result.stdout == ""

def test_directory_as_input(tmp_path):
    """Test script with a directory instead of a file."""
    result = run_script([str(tmp_path)])

    assert result.returncode == 1
    assert "is not a file" in result.stderr
    assert result.stdout == ""

def test_no_arguments():
    """Test script with no arguments."""
    result = run_script([])

    assert result.returncode == 1
    assert "Usage:" in result.stderr
    assert result.stdout == ""

if __name__ == "__main__":
    pytest.main([__file__])
