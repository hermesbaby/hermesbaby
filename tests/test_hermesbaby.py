import subprocess
import sys


def test_entry_points():
    """Test the entry points"""

    expected_stdout = "Hello"
    expected_stderr = ""

    entry_points = {
        "as-module": [sys.executable, "-m", "hermesbaby"],
        "as-script-long": ["poetry", "run", "hermesbaby"],
        "as script-short": ["poetry", "run", "hb"],
    }

    for _, call in entry_points.items():

        result = subprocess.run(
            call,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )

        assert result.returncode == 0, f"Unexpected return code: {result.returncode}"
        assert (
            result.stdout.strip() == expected_stdout
        ), f"Unexpected output: {result.stdout}"
        assert (
            result.stderr.strip() == expected_stderr
        ), f"Unexpected error output: {result.stderr}"
