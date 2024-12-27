import pytest
import os
from pathlib import Path
import subprocess
import sys


entry_points = {
    "as-module": [sys.executable, "-m", "hermesbaby"],
    "as-script-long": ["poetry", "run", "hermesbaby"],
    "as script-short": ["poetry", "run", "hb"],
}


def test_entry_points():
    """Test the entry points"""

    for _, call in entry_points.items():

        result = subprocess.run(
            call,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )

        assert result.returncode == 0, f"Unexpected return code: {result.returncode}"
        assert result.stdout.strip() == "Hello", f"Unexpected output: {result.stdout}"
        assert result.stderr.strip() == "", f"Unexpected error output: {result.stderr}"


@pytest.mark.parametrize(
    "some_rel_path_as_str, option",
    [
        ("", ""),
        (".", ""),
        ("some/relative/path", ""),
        ("", "--template vscode_scratch"),
        (".", "--template vscode_scratch"),
        ("some/relative/path", "--template vscode_scratch"),
    ],
)
def test_task_new(temp_dir, some_rel_path_as_str, option):
    """Test the task new"""
    from src.hermesbaby.__main__ import main

    args = f"new {some_rel_path_as_str} {option}"

    main(args.split())

    some_rel_path = Path(some_rel_path_as_str)
    path_to_index_rst = temp_dir / some_rel_path / "docs" / "index.rst"

    assert path_to_index_rst.exists(), f"Project path does not exist: {project_path}"
