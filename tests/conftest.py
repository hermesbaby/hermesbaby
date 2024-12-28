import pytest
import os
from pathlib import Path
import tempfile
import shutil

from typer.testing import CliRunner


@pytest.fixture(scope="function")
def cli_runner():
    yield CliRunner()


@pytest.fixture(scope="function")
def temp_dir():
    temp_dir_as_str = tempfile.mkdtemp()

    current_dir_as_str = Path.cwd()
    os.chdir(temp_dir_as_str)

    yield Path(temp_dir_as_str)

    os.chdir(current_dir_as_str)
    shutil.rmtree(temp_dir_as_str)
