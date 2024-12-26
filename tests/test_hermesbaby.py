import subprocess
import sys


def test_no_args():
    # Use the installed package directly
    result = subprocess.run(
        [sys.executable, "-m", "hermesbaby"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )

    # Assert the output and return code
    assert result.returncode == 0, f"Unexpected return code: {result.returncode}"
    assert result.stdout.strip() == "Hermesbaby", f"Unexpected output: {result.stdout}"
    assert result.stderr.strip() == "", f"Unexpected error output: {result.stderr}"
